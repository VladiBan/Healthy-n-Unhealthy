import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import google.generativeai as genai
import json
import re
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IngredientIQ",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:ital,wght@0,400;0,500;1,400&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f;
    color: #e8e6e0;
    font-family: 'Syne', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 0%, #1a0a2e 0%, #0a0a0f 50%),
                radial-gradient(ellipse at 80% 100%, #0f1a0a 0%, transparent 60%);
    min-height: 100vh;
}

[data-testid="stHeader"] { display: none; }
[data-testid="stSidebar"] { display: none; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1200px; margin: 0 auto; }

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 4rem 0 3rem;
    position: relative;
}
.hero::before {
    content: '';
    position: absolute;
    top: 0; left: 50%;
    transform: translateX(-50%);
    width: 600px; height: 300px;
    background: radial-gradient(ellipse, rgba(120,80,255,0.15) 0%, transparent 70%);
    pointer-events: none;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.25em;
    color: #7b5fff;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.hero-title {
    font-size: clamp(3rem, 8vw, 5.5rem);
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #ffffff 30%, #b4a0ff 70%, #7b5fff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.75rem;
}
.hero-subtitle {
    font-size: 1.1rem;
    font-weight: 400;
    color: #888;
    letter-spacing: 0.02em;
}

/* ── Upload zone ── */
.upload-section {
    background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(123,95,255,0.05) 100%);
    border: 1px solid rgba(123,95,255,0.2);
    border-radius: 20px;
    padding: 2.5rem;
    margin: 2rem 0;
    position: relative;
    overflow: hidden;
}
.upload-section::before {
    content: '';
    position: absolute;
    top: -1px; left: 10%; right: 10%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(123,95,255,0.6), transparent);
}

/* ── Cards ── */
.card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1.75rem;
    margin: 1rem 0;
    position: relative;
    transition: border-color 0.2s;
}
.card:hover { border-color: rgba(123,95,255,0.3); }

.card-danger {
    background: rgba(255,60,60,0.05);
    border-color: rgba(255,60,60,0.2);
}
.card-danger:hover { border-color: rgba(255,60,60,0.4); }

.card-warning {
    background: rgba(255,180,0,0.05);
    border-color: rgba(255,180,0,0.2);
}
.card-warning:hover { border-color: rgba(255,180,0,0.4); }

.card-safe {
    background: rgba(60,220,120,0.05);
    border-color: rgba(60,220,120,0.2);
}

/* ── Badges ── */
.badge {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.25rem 0.65rem;
    border-radius: 999px;
    margin-bottom: 0.75rem;
}
.badge-danger { background: rgba(255,60,60,0.15); color: #ff6b6b; border: 1px solid rgba(255,60,60,0.3); }
.badge-warning { background: rgba(255,180,0,0.15); color: #ffb400; border: 1px solid rgba(255,180,0,0.3); }
.badge-safe { background: rgba(60,220,120,0.15); color: #3cdc78; border: 1px solid rgba(60,220,120,0.3); }
.badge-info { background: rgba(123,95,255,0.15); color: #b4a0ff; border: 1px solid rgba(123,95,255,0.3); }

/* ── Ingredient name ── */
.ing-name {
    font-size: 1.1rem;
    font-weight: 700;
    color: #f0eee8;
    letter-spacing: -0.01em;
    margin-bottom: 0.4rem;
}
.ing-reason {
    font-size: 0.88rem;
    color: #aaa;
    line-height: 1.6;
    font-family: 'DM Mono', monospace;
    font-style: italic;
}

/* ── OCR text box ── */
.ocr-box {
    background: rgba(0,0,0,0.4);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    color: #888;
    line-height: 1.7;
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 200px;
    overflow-y: auto;
}

/* ── Section headers ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 2rem 0 1rem;
}
.section-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(123,95,255,0.4), transparent);
}
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #7b5fff;
}

/* ── Score ring ── */
.score-container {
    text-align: center;
    padding: 2rem;
}
.score-number {
    font-size: 4rem;
    font-weight: 800;
    letter-spacing: -0.05em;
    line-height: 1;
}
.score-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #666;
    margin-top: 0.5rem;
}

/* ── Streamlit overrides ── */
.stFileUploader > div { 
    background: transparent !important;
    border: none !important;
}
.stFileUploader label { color: #888 !important; font-family: 'Syne', sans-serif !important; }

[data-testid="stFileUploaderDropzone"] {
    background: rgba(123,95,255,0.05) !important;
    border: 2px dashed rgba(123,95,255,0.3) !important;
    border-radius: 12px !important;
    transition: all 0.2s !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    background: rgba(123,95,255,0.1) !important;
    border-color: rgba(123,95,255,0.6) !important;
}

.stButton > button {
    background: linear-gradient(135deg, #7b5fff, #5b3fd4) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.65rem 2rem !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    width: 100%;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #9070ff, #7b5fff) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 30px rgba(123,95,255,0.4) !important;
}

.stSpinner > div { color: #7b5fff !important; }

div[data-testid="column"] { padding: 0 0.5rem; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(123,95,255,0.4); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def load_ocr_reader():
    # 'en' covers all Latin-script languages (DE, FR, ES, IT, NL, PL, RO, HR, TR, etc.)
    # 'bg' + 'ru' add Cyrillic — they share one model so overhead is minimal
    # model_storage_directory persists the download across Streamlit Cloud restarts
    import os
    model_dir = os.path.join(os.path.expanduser("~"), ".EasyOCR")
    os.makedirs(model_dir, exist_ok=True)
    return easyocr.Reader(['en', 'bg', 'ru'], gpu=False, verbose=False,
                          model_storage_directory=model_dir)


def run_ocr(image: Image.Image) -> str:
    reader = load_ocr_reader()
    # Resize if image is huge — reduces memory spike during inference
    max_dim = 2000
    w, h = image.size
    if max(w, h) > max_dim:
        scale = max_dim / max(w, h)
        image = image.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    img_array = np.array(image.convert("RGB"))
    results = reader.readtext(img_array, detail=0, paragraph=True)
    return " ".join(results)


def analyze_ingredients(raw_text: str) -> dict:
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY not found. Add it to your Streamlit secrets.")
        st.stop()

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""You are an expert nutritionist and food-safety researcher.
The text below was extracted via OCR from a product label photograph.
Identify every ingredient or additive mentioned, then for each one rate how harmful it is.

OCR TEXT:
\"\"\"
{raw_text}
\"\"\"

Respond ONLY with valid JSON (no markdown, no extra text) in this exact schema:
{{
  "product_name": "<best guess at product name or 'Unknown'>",
  "overall_score": <integer 0-100 where 100 = perfectly safe, 0 = extremely harmful>,
  "overall_verdict": "<1-sentence summary>",
  "ingredients": [
    {{
      "name": "<ingredient name>",
      "risk_level": "<DANGER|WARNING|SAFE>",
      "reason": "<1-2 sentences: why it is harmful or why it is safe>"
    }}
  ]
}}

Rules:
- DANGER = strongly linked to health harms (carcinogens, endocrine disruptors, severe allergens, banned in some countries, etc.)
- WARNING = moderate concerns, controversial, or problematic in large amounts
- SAFE = generally recognised as safe
- Be factual and cite the mechanism (e.g. "linked to liver toxicity", "may spike blood sugar")
- If no clear ingredients are found, return an empty ingredients array and explain in overall_verdict.
- The OCR text may be noisy or garbled — do your best to interpret it. For mineral water, treat the chemical composition (Na+, K+, Ca2+, F-, Cl-, SO4, HCO3 etc.) as the "ingredients".
- For mineral water or similar products, flag high fluoride (F- above 1.5 mg/L), high sodium, or very high/low pH as WARNING or DANGER where appropriate.
"""

    response = model.generate_content(prompt)
    raw = response.text.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"```$", "", raw).strip()
    return json.loads(raw)


def score_color(score: int) -> str:
    if score >= 70:
        return "#3cdc78"
    elif score >= 40:
        return "#ffb400"
    return "#ff6b6b"


# ── UI ───────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">AI-Powered Label Scanner</div>
  <div class="hero-title">IngredientIQ</div>
  <div class="hero-subtitle">Photograph a product label → know exactly what you're putting in your body</div>
</div>
""", unsafe_allow_html=True)

# Upload
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Drop a photo of a product label (ingredients list works best)",
    type=["jpg", "jpeg", "png", "webp", "bmp"],
    label_visibility="visible",
)
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
        # Step 1 – OCR
        with st.spinner("Reading text from image…"):
            ocr_text = run_ocr(image)

        if not ocr_text.strip():
            st.error("No text could be extracted. Try a clearer, higher-resolution photo.")
            st.stop()

        st.markdown("""
        <div class="section-header">
          <div class="section-label">Extracted text</div>
          <div class="section-line"></div>
        </div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="ocr-box">{ocr_text}</div>', unsafe_allow_html=True)

        # Step 2 – AI analysis
        with st.spinner("Analysing ingredients with Gemini AI…"):
            try:
                result = analyze_ingredients(ocr_text)
            except json.JSONDecodeError:
                st.error("Could not parse the AI response. Please try again.")
                st.stop()

        # ── Results header ──
        st.markdown("""
        <div class="section-header" style="margin-top:2.5rem">
          <div class="section-label">Analysis results</div>
          <div class="section-line"></div>
        </div>""", unsafe_allow_html=True)

        score = result.get("overall_score", 50)
        color = score_color(score)

        col_score, col_verdict = st.columns([1, 3])

        with col_score:
            st.markdown(f"""
            <div class="card score-container">
              <div class="score-number" style="color:{color}">{score}</div>
              <div class="score-label">Safety Score / 100</div>
            </div>""", unsafe_allow_html=True)

        with col_verdict:
            pname = result.get("product_name", "Unknown product")
            verdict = result.get("overall_verdict", "")
            st.markdown(f"""
            <div class="card" style="height:100%">
              <span class="badge badge-info">Product</span>
              <div class="ing-name" style="font-size:1.4rem">{pname}</div>
              <p style="color:#aaa;line-height:1.7;margin-top:0.75rem;font-size:0.95rem">{verdict}</p>
            </div>""", unsafe_allow_html=True)

        # ── Ingredient cards ──
        ingredients = result.get("ingredients", [])

        danger = [i for i in ingredients if i.get("risk_level") == "DANGER"]
        warning = [i for i in ingredients if i.get("risk_level") == "WARNING"]
        safe = [i for i in ingredients if i.get("risk_level") == "SAFE"]

        if danger:
            st.markdown("""
            <div class="section-header">
              <div class="section-label">🚨 Avoid these</div>
              <div class="section-line"></div>
            </div>""", unsafe_allow_html=True)
            cols = st.columns(2)
            for idx, ing in enumerate(danger):
                with cols[idx % 2]:
                    st.markdown(f"""
                    <div class="card card-danger">
                      <span class="badge badge-danger">Danger</span>
                      <div class="ing-name">{ing['name']}</div>
                      <div class="ing-reason">{ing['reason']}</div>
                    </div>""", unsafe_allow_html=True)

        if warning:
            st.markdown("""
            <div class="section-header">
              <div class="section-label">⚠️ Use caution</div>
              <div class="section-line"></div>
            </div>""", unsafe_allow_html=True)
            cols = st.columns(2)
            for idx, ing in enumerate(warning):
                with cols[idx % 2]:
                    st.markdown(f"""
                    <div class="card card-warning">
                      <span class="badge badge-warning">Warning</span>
                      <div class="ing-name">{ing['name']}</div>
                      <div class="ing-reason">{ing['reason']}</div>
                    </div>""", unsafe_allow_html=True)

        if safe:
            st.markdown("""
            <div class="section-header">
              <div class="section-label">✅ Generally safe</div>
              <div class="section-line"></div>
            </div>""", unsafe_allow_html=True)
            cols = st.columns(3)
            for idx, ing in enumerate(safe):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="card card-safe">
                      <span class="badge badge-safe">Safe</span>
                      <div class="ing-name">{ing['name']}</div>
                      <div class="ing-reason">{ing['reason']}</div>
                    </div>""", unsafe_allow_html=True)

        if not ingredients:
            st.info("No recognisable ingredients were found. Try a clearer photo focused on the ingredients list.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <p style="text-align:center;color:#444;font-family:'DM Mono',monospace;font-size:0.72rem;letter-spacing:0.08em">
          FOR INFORMATIONAL PURPOSES ONLY — NOT MEDICAL ADVICE
        </p>""", unsafe_allow_html=True)
