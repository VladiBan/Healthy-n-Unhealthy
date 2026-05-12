import streamlit as st
from PIL import Image
import pytesseract
import re

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="IngredientIQ", page_icon="🔬", layout="wide", initial_sidebar_state="collapsed")

# ── Ingredient database ───────────────────────────────────────────────────────
INGREDIENT_DB = [
    # DANGER
    {"name": "Aspartame (E951)", "risk_level": "DANGER", "aliases": ["aspartame", "e951", "е951"], "reason": "Artificial sweetener classified as possibly carcinogenic (Group 2B) by IARC in 2023; linked to headaches and mood disorders."},
    {"name": "Sodium Nitrite (E250)", "risk_level": "DANGER", "aliases": ["sodium nitrite", "e250", "е250", "натриев нитрит"], "reason": "Preservative in processed meats that forms nitrosamines in the body — potent carcinogens strongly linked to colorectal cancer."},
    {"name": "Sodium Nitrate (E251)", "risk_level": "DANGER", "aliases": ["sodium nitrate", "e251", "е251", "натриев нитрат"], "reason": "Converts to nitrosamines in the gut; strongly linked to colorectal and stomach cancer."},
    {"name": "Potassium Bromate (E924)", "risk_level": "DANGER", "aliases": ["potassium bromate", "e924", "е924"], "reason": "Banned in the EU, UK, and Canada. Classified as a possible human carcinogen; damages kidneys and nervous system."},
    {"name": "Titanium Dioxide (E171)", "risk_level": "DANGER", "aliases": ["titanium dioxide", "e171", "е171", "титанов диоксид"], "reason": "Banned as a food additive in the EU since 2022. Nanoparticles may damage DNA and accumulate in organs."},
    {"name": "Red 40 / Allura Red (E129)", "risk_level": "DANGER", "aliases": ["allura red", "red 40", "e129", "е129"], "reason": "Linked to hyperactivity in children; contains benzidine, a known human carcinogen. Requires warning labels in the EU."},
    {"name": "Yellow 5 / Tartrazine (E102)", "risk_level": "DANGER", "aliases": ["tartrazine", "yellow 5", "e102", "е102"], "reason": "Linked to hyperactivity in children and allergic reactions. Requires a warning label in the EU."},
    {"name": "Yellow 6 / Sunset Yellow (E110)", "risk_level": "DANGER", "aliases": ["sunset yellow", "yellow 6", "e110", "е110"], "reason": "Associated with hyperactivity in children and adrenal tumours in animal studies. EU warning label required."},
    {"name": "High Fructose Corn Syrup", "risk_level": "DANGER", "aliases": ["high fructose corn syrup", "hfcs", "glucose-fructose syrup", "glucose fructose syrup", "глюкозо-фруктозен сироп"], "reason": "Strongly linked to obesity, type 2 diabetes, and non-alcoholic fatty liver disease."},
    {"name": "Trans Fats / Partially Hydrogenated Oils", "risk_level": "DANGER", "aliases": ["partially hydrogenated", "trans fat", "трансмазнини"], "reason": "Raise LDL cholesterol, lower HDL; strongly linked to cardiovascular disease. Banned in many countries."},
    {"name": "Acesulfame K (E950)", "risk_level": "DANGER", "aliases": ["acesulfame", "ace-k", "e950", "е950", "ацесулфам"], "reason": "Artificial sweetener that may disrupt gut microbiome; shown potential carcinogenic effects in animal studies."},
    {"name": "Saccharin (E954)", "risk_level": "DANGER", "aliases": ["saccharin", "e954", "е954", "захарин"], "reason": "Linked to bladder cancer in animal studies; may disrupt insulin response and gut bacteria."},
    {"name": "BHA / Butylated Hydroxyanisole (E320)", "risk_level": "DANGER", "aliases": ["butylated hydroxyanisole", "bha", "e320", "е320"], "reason": "Classified as possibly carcinogenic to humans (Group 2B) by IARC; endocrine disruptor."},
    {"name": "Carrageenan (E407)", "risk_level": "DANGER", "aliases": ["carrageenan", "e407", "е407", "карагенан"], "reason": "May trigger intestinal inflammation and ulcers; linked to tumour promotion in animal studies."},
    {"name": "Fluoride (F⁻)", "risk_level": "DANGER", "aliases": ["fluoride", "fluor", "флуорид", "флуор"], "reason": "Above 1.5 mg/L (WHO guideline) causes dental and skeletal fluorosis; neurotoxic at high levels. Not suitable for infants."},
    {"name": "Brominated Vegetable Oil (BVO)", "risk_level": "DANGER", "aliases": ["brominated vegetable oil", "bvo"], "reason": "Banned in the EU and Japan. Bromine accumulates in body fat and is linked to thyroid disruption and neurological damage."},
    {"name": "Propyl Paraben (E216)", "risk_level": "DANGER", "aliases": ["propyl paraben", "e216", "е216", "propylparaben"], "reason": "Endocrine disruptor that mimics oestrogen; linked to reproductive toxicity. Banned in EU food products."},
    # WARNING
    {"name": "Sodium / High Sodium (Na⁺)", "risk_level": "WARNING", "aliases": ["sodium", "натрий", "na+"], "reason": "Essential mineral but excess sodium (>2300 mg/day) raises blood pressure and increases cardiovascular risk."},
    {"name": "MSG / Monosodium Glutamate (E621)", "risk_level": "WARNING", "aliases": ["monosodium glutamate", "msg", "e621", "е621", "глутамат"], "reason": "Some people report headaches and flushing; may stimulate overeating by enhancing palatability."},
    {"name": "Sodium Benzoate (E211)", "risk_level": "WARNING", "aliases": ["sodium benzoate", "e211", "е211", "натриев бензоат"], "reason": "Can react with vitamin C to form benzene, a known carcinogen; linked to hyperactivity in children."},
    {"name": "Sulphites / Sulfur Dioxide (E220-E228)", "risk_level": "WARNING", "aliases": ["sulphite", "sulfite", "sulphur dioxide", "sulfur dioxide", "e220", "e221", "e222", "e223", "e224", "серен диоксид"], "reason": "Can trigger severe asthma attacks and allergic reactions in sensitive individuals; destroys vitamin B1."},
    {"name": "Phosphoric Acid (E338)", "risk_level": "WARNING", "aliases": ["phosphoric acid", "e338", "е338", "фосфорна киселина"], "reason": "Leaches calcium from bones over time; linked to reduced bone density and kidney stones with high consumption."},
    {"name": "Caramel Colour IV (E150d)", "risk_level": "WARNING", "aliases": ["caramel colour", "caramel color", "e150d", "карамелен цвят"], "reason": "Class IV caramel contains 4-MEI, a possible carcinogen found in many cola drinks."},
    {"name": "Sucralose (E955)", "risk_level": "WARNING", "aliases": ["sucralose", "e955", "е955", "сукралоза"], "reason": "May alter gut microbiome composition and reduce insulin sensitivity; recent studies suggest possible DNA damage at high doses."},
    {"name": "BHT / Butylated Hydroxytoluene (E321)", "risk_level": "WARNING", "aliases": ["butylated hydroxytoluene", "bht", "e321", "е321"], "reason": "Some evidence of tumour promotion in animal studies at high doses; possible endocrine disruptor."},
    {"name": "Potassium Sorbate (E202)", "risk_level": "WARNING", "aliases": ["potassium sorbate", "e202", "е202", "калиев сорбат"], "reason": "Generally safe but can trigger allergic skin reactions; may damage DNA of white blood cells in vitro."},
    {"name": "Xanthan Gum (E415)", "risk_level": "WARNING", "aliases": ["xanthan", "e415", "е415", "ксантан"], "reason": "Can cause bloating and diarrhoea in sensitive individuals, especially in large amounts."},
    {"name": "High pH / Very Alkaline", "risk_level": "WARNING", "aliases": ["ph 8.", "ph 9.", "ph 10", "рн 8", "рн 9", "рн 10"], "reason": "pH above 8.5 may neutralise stomach acid, impairing digestion and reducing absorption of minerals and medications."},
    {"name": "Caffeine", "risk_level": "WARNING", "aliases": ["caffeine", "кофеин"], "reason": "Stimulant that can cause anxiety, insomnia, and heart palpitations; addictive; not safe for children or pregnant women."},
    {"name": "Refined Sugar / Sucrose", "risk_level": "WARNING", "aliases": ["sugar", "sucrose", "захар", "захароза", "zucker"], "reason": "Excess consumption linked to obesity, type 2 diabetes, tooth decay, and chronic inflammation."},
    {"name": "Palm Oil", "risk_level": "WARNING", "aliases": ["palm oil", "палмово масло", "palmol", "huile de palme"], "reason": "High in saturated fat; processing produces glycidyl esters which are possible carcinogens."},
    {"name": "Artificial Flavours", "risk_level": "WARNING", "aliases": ["artificial flavour", "artificial flavor", "artificial flavoring", "изкуствен аромат"], "reason": "Broad category of untested long-term compounds; may mask poor ingredient quality."},
    {"name": "Sorbitol (E420)", "risk_level": "WARNING", "aliases": ["sorbitol", "e420", "е420", "сорбитол"], "reason": "Can cause bloating, gas, and diarrhoea; laxative effect above ~20g/day."},
    {"name": "Calcium Propionate (E282)", "risk_level": "WARNING", "aliases": ["calcium propionate", "e282", "е282"], "reason": "Preservative linked to behavioural changes and irritability in children in some studies."},
    # SAFE
    {"name": "Water", "risk_level": "SAFE", "aliases": ["water", "вода", "wasser", "eau", "aqua"], "reason": "Essential for life. Safe for consumption."},
    {"name": "Vitamin C / Ascorbic Acid (E300)", "risk_level": "SAFE", "aliases": ["ascorbic acid", "vitamin c", "e300", "е300", "аскорбинова киселина"], "reason": "Essential antioxidant vitamin; supports immune function and collagen synthesis."},
    {"name": "Vitamin E / Tocopherol (E306-309)", "risk_level": "SAFE", "aliases": ["tocopherol", "vitamin e", "e306", "e307", "e308", "e309", "токоферол"], "reason": "Natural antioxidant protecting cell membranes from oxidative damage."},
    {"name": "Citric Acid (E330)", "risk_level": "SAFE", "aliases": ["citric acid", "e330", "е330", "лимонена киселина"], "reason": "Naturally occurring in citrus fruits; safe preservative and flavour enhancer."},
    {"name": "Lactic Acid (E270)", "risk_level": "SAFE", "aliases": ["lactic acid", "e270", "е270", "млечна киселина"], "reason": "Naturally produced in fermentation; safe preservative and pH regulator."},
    {"name": "Pectin (E440)", "risk_level": "SAFE", "aliases": ["pectin", "e440", "е440", "пектин"], "reason": "Natural dietary fibre from fruit; may help lower cholesterol and blood sugar."},
    {"name": "Calcium (Ca²⁺)", "risk_level": "SAFE", "aliases": ["calcium", "калций", "ca2+"], "reason": "Essential mineral for bone health, muscle function, and nerve signalling."},
    {"name": "Potassium (K⁺)", "risk_level": "SAFE", "aliases": ["potassium", "калий"], "reason": "Essential electrolyte for heart rhythm, muscle function, and blood pressure regulation."},
    {"name": "Magnesium (Mg²⁺)", "risk_level": "SAFE", "aliases": ["magnesium", "магнезий", "mg2+"], "reason": "Essential mineral involved in 300+ enzymatic reactions; supports muscle and nerve function."},
    {"name": "Bicarbonate / HCO₃⁻", "risk_level": "SAFE", "aliases": ["bicarbonate", "hco3", "бикарбонат", "hydrogen carbonate"], "reason": "Natural mineral pH buffer; may aid digestion and reduce acidity."},
    {"name": "Zinc (Zn)", "risk_level": "SAFE", "aliases": ["zinc", "цинк", "zn "], "reason": "Essential trace mineral for immune function, wound healing, and enzyme activity."},
    {"name": "Chloride (Cl⁻)", "risk_level": "SAFE", "aliases": ["chloride", "хлорид", "cl-"], "reason": "Essential electrolyte for fluid balance and stomach acid production."},
    {"name": "Sulphate (SO₄²⁻)", "risk_level": "SAFE", "aliases": ["sulphate", "sulfate", "so4", "сулфат"], "reason": "Naturally occurring mineral ion; helps with digestion and detoxification at normal levels."},
    {"name": "Lecithin (E322)", "risk_level": "SAFE", "aliases": ["lecithin", "e322", "е322", "лецитин"], "reason": "Natural emulsifier from soy or sunflower; supports brain health and is well tolerated."},
    {"name": "Citric Acid (E330)", "risk_level": "SAFE", "aliases": ["citric acid", "e330", "лимонена киселина"], "reason": "Naturally occurring in citrus; safe preservative and flavour enhancer."},
    {"name": "Natural Flavours", "risk_level": "SAFE", "aliases": ["natural flavour", "natural flavor", "натурален аромат"], "reason": "Derived from natural sources; generally considered safe."},
    {"name": "Sunflower Oil", "risk_level": "SAFE", "aliases": ["sunflower oil", "слънчогледово масло", "sonnenblumenol"], "reason": "Rich in vitamin E and unsaturated fats; healthy in moderate amounts."},
    {"name": "Olive Oil", "risk_level": "SAFE", "aliases": ["olive oil", "зехтин", "olivenol"], "reason": "Rich in monounsaturated fats and polyphenols; strongly associated with cardiovascular benefits."},
]


def run_ocr(image: Image.Image) -> str:
    max_dim = 1800
    w, h = image.size
    if max(w, h) > max_dim:
        scale = max_dim / max(w, h)
        image = image.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    try:
        text = pytesseract.image_to_string(image.convert("RGB"), lang="eng+bul+rus+deu+fra")
    except Exception:
        try:
            text = pytesseract.image_to_string(image.convert("RGB"), lang="eng")
        except Exception:
            text = ""
    return text


def match_ingredients(ocr_text: str) -> list:
    text_lower = ocr_text.lower()
    found, seen = [], set()
    for entry in INGREDIENT_DB:
        for alias in entry["aliases"]:
            if alias in text_lower and entry["name"] not in seen:
                found.append(entry)
                seen.add(entry["name"])
                break
    return found


def overall_score(ingredients: list) -> int:
    if not ingredients:
        return 70
    danger  = sum(1 for i in ingredients if i["risk_level"] == "DANGER")
    warning = sum(1 for i in ingredients if i["risk_level"] == "WARNING")
    return max(0, min(100, 100 - danger * 20 - warning * 7))


def score_color(score: int) -> str:
    return "#3cdc78" if score >= 70 else ("#ffb400" if score >= 40 else "#ff6b6b")


def overall_verdict(score: int, ingredients: list) -> str:
    danger  = sum(1 for i in ingredients if i["risk_level"] == "DANGER")
    warning = sum(1 for i in ingredients if i["risk_level"] == "WARNING")
    if not ingredients:
        return "No known ingredients detected — try a clearer photo of the ingredients list."
    if danger == 0 and warning == 0:
        return f"All {len(ingredients)} detected ingredients are considered safe."
    parts = []
    if danger:  parts.append(f"{danger} harmful ingredient{'s' if danger > 1 else ''}")
    if warning: parts.append(f"{warning} cautionary ingredient{'s' if warning > 1 else ''}")
    return f"Found {' and '.join(parts)} — review the details below."


# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:ital,wght@0,400;0,500;1,400&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,[data-testid="stAppViewContainer"]{background:#0a0a0f;color:#e8e6e0;font-family:'Syne',sans-serif}
[data-testid="stAppViewContainer"]{background:radial-gradient(ellipse at 20% 0%,#1a0a2e 0%,#0a0a0f 50%),radial-gradient(ellipse at 80% 100%,#0f1a0a 0%,transparent 60%);min-height:100vh}
[data-testid="stHeader"],[data-testid="stSidebar"]{display:none}
.block-container{padding:2rem 3rem 4rem;max-width:1200px;margin:0 auto}
.hero{text-align:center;padding:4rem 0 3rem;position:relative}
.hero::before{content:'';position:absolute;top:0;left:50%;transform:translateX(-50%);width:600px;height:300px;background:radial-gradient(ellipse,rgba(120,80,255,.15) 0%,transparent 70%);pointer-events:none}
.hero-eyebrow{font-family:'DM Mono',monospace;font-size:.75rem;letter-spacing:.25em;color:#7b5fff;text-transform:uppercase;margin-bottom:1rem}
.hero-title{font-size:clamp(3rem,8vw,5.5rem);font-weight:800;line-height:1;letter-spacing:-.03em;background:linear-gradient(135deg,#fff 30%,#b4a0ff 70%,#7b5fff 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:.75rem}
.hero-subtitle{font-size:1.1rem;font-weight:400;color:#888;letter-spacing:.02em}
.upload-section{background:linear-gradient(135deg,rgba(255,255,255,.03) 0%,rgba(123,95,255,.05) 100%);border:1px solid rgba(123,95,255,.2);border-radius:20px;padding:2.5rem;margin:2rem 0;position:relative;overflow:hidden}
.upload-section::before{content:'';position:absolute;top:-1px;left:10%;right:10%;height:1px;background:linear-gradient(90deg,transparent,rgba(123,95,255,.6),transparent)}
.card{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:16px;padding:1.75rem;margin:1rem 0;transition:border-color .2s}
.card:hover{border-color:rgba(123,95,255,.3)}
.card-danger{background:rgba(255,60,60,.05);border-color:rgba(255,60,60,.2)}.card-danger:hover{border-color:rgba(255,60,60,.4)}
.card-warning{background:rgba(255,180,0,.05);border-color:rgba(255,180,0,.2)}.card-warning:hover{border-color:rgba(255,180,0,.4)}
.card-safe{background:rgba(60,220,120,.05);border-color:rgba(60,220,120,.2)}
.badge{display:inline-block;font-family:'DM Mono',monospace;font-size:.65rem;font-weight:500;letter-spacing:.1em;text-transform:uppercase;padding:.25rem .65rem;border-radius:999px;margin-bottom:.75rem}
.badge-danger{background:rgba(255,60,60,.15);color:#ff6b6b;border:1px solid rgba(255,60,60,.3)}
.badge-warning{background:rgba(255,180,0,.15);color:#ffb400;border:1px solid rgba(255,180,0,.3)}
.badge-safe{background:rgba(60,220,120,.15);color:#3cdc78;border:1px solid rgba(60,220,120,.3)}
.badge-info{background:rgba(123,95,255,.15);color:#b4a0ff;border:1px solid rgba(123,95,255,.3)}
.ing-name{font-size:1.1rem;font-weight:700;color:#f0eee8;letter-spacing:-.01em;margin-bottom:.4rem}
.ing-reason{font-size:.88rem;color:#aaa;line-height:1.6;font-family:'DM Mono',monospace;font-style:italic}
.section-header{display:flex;align-items:center;gap:.75rem;margin:2rem 0 1rem}
.section-line{flex:1;height:1px;background:linear-gradient(90deg,rgba(123,95,255,.4),transparent)}
.section-label{font-family:'DM Mono',monospace;font-size:.7rem;letter-spacing:.2em;text-transform:uppercase;color:#7b5fff}
.score-container{text-align:center;padding:2rem}
.score-number{font-size:4rem;font-weight:800;letter-spacing:-.05em;line-height:1}
.score-label{font-family:'DM Mono',monospace;font-size:.7rem;letter-spacing:.15em;text-transform:uppercase;color:#666;margin-top:.5rem}
.ocr-box{background:rgba(0,0,0,.4);border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:1.25rem 1.5rem;font-family:'DM Mono',monospace;font-size:.82rem;color:#888;line-height:1.7;white-space:pre-wrap;word-break:break-word;max-height:200px;overflow-y:auto}
.stFileUploader>div{background:transparent!important;border:none!important}
.stFileUploader label{color:#888!important;font-family:'Syne',sans-serif!important}
[data-testid="stFileUploaderDropzone"]{background:rgba(123,95,255,.05)!important;border:2px dashed rgba(123,95,255,.3)!important;border-radius:12px!important;transition:all .2s!important}
[data-testid="stFileUploaderDropzone"]:hover{background:rgba(123,95,255,.1)!important;border-color:rgba(123,95,255,.6)!important}
.stButton>button{background:linear-gradient(135deg,#7b5fff,#5b3fd4)!important;color:#fff!important;border:none!important;border-radius:10px!important;font-family:'Syne',sans-serif!important;font-weight:700!important;font-size:.95rem!important;letter-spacing:.05em!important;padding:.65rem 2rem!important;cursor:pointer!important;transition:all .2s!important;width:100%}
.stButton>button:hover{background:linear-gradient(135deg,#9070ff,#7b5fff)!important;transform:translateY(-1px)!important;box-shadow:0 8px 30px rgba(123,95,255,.4)!important}
.stSpinner>div{color:#7b5fff!important}
div[data-testid="column"]{padding:0 .5rem}
::-webkit-scrollbar{width:4px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:rgba(123,95,255,.4);border-radius:2px}
</style>
""", unsafe_allow_html=True)

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">Label Scanner — No AI, 100% Free</div>
  <div class="hero-title">IngredientIQ</div>
  <div class="hero-subtitle">Photograph a product label → instantly know what's harmful and why</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="upload-section">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Drop a photo of a product label (ingredients side works best)", type=["jpg","jpeg","png","webp","bmp"], label_visibility="visible")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    image = Image.open(uploaded_file)
    col_img, col_btn = st.columns([3, 1])
    with col_img:
        st.image(image, caption="Uploaded label", width="stretch")
    with col_btn:
        st.markdown("<br><br>", unsafe_allow_html=True)
        analyse = st.button("🔬  Analyse Ingredients")

    if analyse:
        with st.spinner("Reading text from image…"):
            ocr_text = run_ocr(image)

        st.markdown("""<div class="section-header"><div class="section-label">Extracted text</div><div class="section-line"></div></div>""", unsafe_allow_html=True)
        if ocr_text.strip():
            st.markdown(f'<div class="ocr-box">{ocr_text}</div>', unsafe_allow_html=True)
        else:
            st.warning("Could not extract text. Try a clearer, better-lit photo of the ingredients list.")

        with st.spinner("Checking ingredient database…"):
            matched = match_ingredients(ocr_text)

        score   = overall_score(matched)
        color   = score_color(score)
        verdict = overall_verdict(score, matched)

        st.markdown("""<div class="section-header" style="margin-top:2.5rem"><div class="section-label">Analysis results</div><div class="section-line"></div></div>""", unsafe_allow_html=True)

        col_score, col_v = st.columns([1, 3])
        with col_score:
            st.markdown(f'<div class="card score-container"><div class="score-number" style="color:{color}">{score}</div><div class="score-label">Safety Score / 100</div></div>', unsafe_allow_html=True)
        with col_v:
            st.markdown(f'''<div class="card" style="height:100%">
              <span class="badge badge-info">Verdict</span>
              <p style="color:#aaa;line-height:1.7;margin-top:.5rem;font-size:.95rem">{verdict}</p>
              <p style="color:#555;font-family:'DM Mono',monospace;font-size:.72rem;margin-top:1rem">Matched {len(matched)} ingredient{"s" if len(matched)!=1 else ""} from database of {len(INGREDIENT_DB)} entries</p>
            </div>''', unsafe_allow_html=True)

        danger_list  = [i for i in matched if i["risk_level"] == "DANGER"]
        warning_list = [i for i in matched if i["risk_level"] == "WARNING"]
        safe_list    = [i for i in matched if i["risk_level"] == "SAFE"]

        if danger_list:
            st.markdown("""<div class="section-header"><div class="section-label">🚨 Avoid these</div><div class="section-line"></div></div>""", unsafe_allow_html=True)
            cols = st.columns(2)
            for idx, ing in enumerate(danger_list):
                with cols[idx % 2]:
                    st.markdown(f'<div class="card card-danger"><span class="badge badge-danger">Danger</span><div class="ing-name">{ing["name"]}</div><div class="ing-reason">{ing["reason"]}</div></div>', unsafe_allow_html=True)

        if warning_list:
            st.markdown("""<div class="section-header"><div class="section-label">⚠️ Use caution</div><div class="section-line"></div></div>""", unsafe_allow_html=True)
            cols = st.columns(2)
            for idx, ing in enumerate(warning_list):
                with cols[idx % 2]:
                    st.markdown(f'<div class="card card-warning"><span class="badge badge-warning">Warning</span><div class="ing-name">{ing["name"]}</div><div class="ing-reason">{ing["reason"]}</div></div>', unsafe_allow_html=True)

        if safe_list:
            st.markdown("""<div class="section-header"><div class="section-label">✅ Generally safe</div><div class="section-line"></div></div>""", unsafe_allow_html=True)
            cols = st.columns(3)
            for idx, ing in enumerate(safe_list):
                with cols[idx % 3]:
                    st.markdown(f'<div class="card card-safe"><span class="badge badge-safe">Safe</span><div class="ing-name">{ing["name"]}</div><div class="ing-reason">{ing["reason"]}</div></div>', unsafe_allow_html=True)

        if not matched:
            st.info("No ingredients from our database were detected. Try a clearer photo, or the product may use ingredients not yet in our database.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p style="text-align:center;color:#444;font-family:\'DM Mono\',monospace;font-size:.72rem;letter-spacing:.08em">FOR INFORMATIONAL PURPOSES ONLY — NOT MEDICAL ADVICE</p>', unsafe_allow_html=True)
