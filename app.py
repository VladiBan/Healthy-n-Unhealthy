import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import json
import re
import os
import io
import base64

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
.card-danger { background: rgba(255,60,60,0.05); border-color: rgba(255,60,60,0.2); }
.card-danger:hover { border-color: rgba(255,60,60,0.4); }
.card-warning { background: rgba(255,180,0,0.05); border-color: rgba(255,180,0,0.2); }
.card-warning:hover { border-color: rgba(255,180,0,0.4); }
.card-safe { background: rgba(60,220,120,0.05); border-color: rgba(60,220,120,0.2); }

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

.score-container { text-align: center; padding: 2rem; }
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

.stFileUploader > div { background: transparent !important; border: none !important; }
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
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(123,95,255,0.4); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_gemini_client():
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY not found. Add it to your Streamlit secrets.")
        st.stop()
    return genai.Client(api_key=api_key)


def image_to_bytes(image: Image.Image) -> bytes:
    # Resize large images to save API bandwidth
    max_dim = 1600
    w, h = image.size
    if max(w, h) > max_dim:
        scale = max_dim / max(w, h)
        image = image.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def analyze_image(image: Image.Image) -> dict:
    client = get_gemini_client()
    img_bytes = image_to_bytes(image)

    prompt = """You are an expert nutritionist and food-safety researcher.
Look at this product label image carefully. Read ALL text visible on the label — including any language (Bulgarian, English, Russian, German, etc.).
Identify every ingredient, additive, or chemical compound listed, then rate how harmful each one is.

Respond ONLY with valid JSON (no markdown, no extra text) in this exact schema:
{
  "product_name": "<best guess at product name or 'Unknown'>",
  "overall_score": <integer 0-100 where 100 = perfectly safe, 0 = extremely harmful>,
  "overall_verdict": "<1-sentence summary>",
  "extracted_text": "<the key text you read from the label>",
  "ingredients": [
    {
      "name": "<ingredient name in English>",
      "risk_level": "<DANGER|WARNING|SAFE>",
      "reason": "<1-2 sentences: why it is harmful or why it is safe>"
    }
  ]
}

Rules:
- DANGER = strongly linked to health harms (carcinogens, endocrine disruptors, severe allergens, banned in some countries)
- WARNING = moderate concerns, controversial, or problematic in large amounts
- SAFE = generally recognised as safe
- Be factual and cite the mechanism (e.g. "linked to liver toxicity", "may spike blood sugar")
- For mineral water, treat the chemical composition (Na+, K+, Ca2+, F-, Cl-, SO4, HCO3 etc.) as ingredients
- Flag high fluoride (F- above 1.5 mg/L), high sodium, or very high/low pH as WARNING or DANGER
- If no ingredients found, return empty array and explain in overall_verdict
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
            types.Part.from_text(text=prompt),
        ],
    )

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
        with st.spinner("Scanning label with Gemini Vision…"):
            try:
                result = analyze_image(image)
            except json.JSONDecodeError:
                st.error("Could not parse the AI response. Please try again.")
                st.stop()
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()

        # Show extracted text
        extracted = result.get("extracted_text", "")
        if extracted:
            st.markdown("""
            <div class="section-header">
              <div class="section-label">Text read from label</div>
              <div class="section-line"></div>
            </div>""", unsafe_allow_html=True)
            st.markdown(f'<div style="background:rgba(0,0,0,0.4);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:1.25rem 1.5rem;font-family:DM Mono,monospace;font-size:0.82rem;color:#888;line-height:1.7;max-height:200px;overflow-y:auto">{extracted}</div>', unsafe_allow_html=True)

        # Results
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

        ingredients = result.get("ingredients", [])
        danger  = [i for i in ingredients if i.get("risk_level") == "DANGER"]
        warning = [i for i in ingredients if i.get("risk_level") == "WARNING"]
        safe    = [i for i in ingredients if i.get("risk_level") == "SAFE"]

        if danger:
            st.markdown("""<div class="section-header"><div class="section-label">🚨 Avoid these</div><div class="section-line"></div></div>""", unsafe_allow_html=True)
            cols = st.columns(2)
            for idx, ing in enumerate(danger):
                with cols[idx % 2]:
                    st.markdown(f"""<div class="card card-danger"><span class="badge badge-danger">Danger</span><div class="ing-name">{ing['name']}</div><div class="ing-reason">{ing['reason']}</div></div>""", unsafe_allow_html=True)

        if warning:
            st.markdown("""<div class="section-header"><div class="section-label">⚠️ Use caution</div><div class="section-line"></div></div>""", unsafe_allow_html=True)
            cols = st.columns(2)
            for idx, ing in enumerate(warning):
                with cols[idx % 2]:
                    st.markdown(f"""<div class="card card-warning"><span class="badge badge-warning">Warning</span><div class="ing-name">{ing['name']}</div><div class="ing-reason">{ing['reason']}</div></div>""", unsafe_allow_html=True)

        if safe:
            st.markdown("""<div class="section-header"><div class="section-label">✅ Generally safe</div><div class="section-line"></div></div>""", unsafe_allow_html=True)
            cols = st.columns(3)
            for idx, ing in enumerate(safe):
                with cols[idx % 3]:
                    st.markdown(f"""<div class="card card-safe"><span class="badge badge-safe">Safe</span><div class="ing-name">{ing['name']}</div><div class="ing-reason">{ing['reason']}</div></div>""", unsafe_allow_html=True)

        if not ingredients:
            st.info("No recognisable ingredients were found. Try a clearer photo focused on the ingredients list.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""<p style="text-align:center;color:#444;font-family:'DM Mono',monospace;font-size:0.72rem;letter-spacing:0.08em">FOR INFORMATIONAL PURPOSES ONLY — NOT MEDICAL ADVICE</p>""", unsafe_allow_html=True)
        
