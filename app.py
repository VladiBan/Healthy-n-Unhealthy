import streamlit as st
from PIL import Image
import numpy as np
import cv2
import re

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IngredientIQ",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────
# EASYOCR READER — cached so it only loads once
# ─────────────────────────────────────────────────────────────
@st.cache_resource
def load_reader():
    import easyocr
    return easyocr.Reader(['en', 'bg'], gpu=False)

# ─────────────────────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────────────────────
INGREDIENT_DB = [
    {
        "name": "Fluoride (F⁻)",
        "risk_level": "DANGER",
        "aliases": ["fluoride", "fluor", "флуорид", "флуор", "f-"],
        "reason": "Above 1.5 mg/L may cause fluorosis and neurological harm. Not suitable for infants."
    },
    {
        "name": "High pH / Very Alkaline",
        "risk_level": "WARNING",
        "aliases": [
            "ph 8", "ph 9", "ph 10", "рн 8", "рн 9", "рн 10",
            "ph9", "ph 9.3", "ph 9.37"
        ],
        "reason": "Very alkaline water may reduce stomach acidity and affect digestion."
    },


    
    {
        "name": "Sodium / High Sodium (Na⁺)",
        "risk_level": "WARNING",
        "aliases": ["sodium", "na+", "натрий"],
        "reason": "Excess sodium intake increases blood pressure and cardiovascular risk."
    },
    {
        "name": "Calcium (Ca²⁺)",
        "risk_level": "SAFE",
        "aliases": ["calcium", "ca2+", "калций"],
        "reason": "Essential mineral supporting bones and muscle function."
    },
    {
        "name": "Potassium (K⁺)",
        "risk_level": "SAFE",
        "aliases": ["potassium", "k+", "калий"],
        "reason": "Important electrolyte for heart and nerve function."
    },
    {
        "name": "Bicarbonate / HCO₃⁻",
        "risk_level": "SAFE",
        "aliases": ["hco3", "bicarbonate", "бикарбонат"],
        "reason": "Natural mineral buffer found in mineral water."
    },
    {
        "name": "Chloride (Cl⁻)",
        "risk_level": "SAFE",
        "aliases": ["chloride", "cl-", "хлорид"],
        "reason": "Essential electrolyte supporting hydration."
    },
    {
        "name": "Sulphate (SO₄²⁻)",
        "risk_level": "SAFE",
        "aliases": ["sulphate", "sulfate", "so4", "сулфат"],
        "reason": "Naturally occurring mineral ion."
    },
    {
        "name": "Zinc (Zn)",
        "risk_level": "SAFE",
        "aliases": ["zinc", "zn", "цинк"],
        "reason": "Essential trace mineral supporting immunity."
    }
]

# ─────────────────────────────────────────────────────────────
# OCR
# ─────────────────────────────────────────────────────────────
def preprocess_image(image: Image.Image):
    img = np.array(image.convert("RGB"))

    scale = 2
    img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    h, w = img.shape[:2]
    x1, x2 = int(w * 0.15), int(w * 0.88)
    y1, y2 = int(h * 0.08), int(h * 0.78)
    img = img[y1:y2, x1:x2]

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.equalizeHist(gray)

    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    gray = cv2.filter2D(gray, -1, kernel)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    return thresh


def run_ocr(image: Image.Image):
    reader = load_reader()
    processed = preprocess_image(image)
    results = reader.readtext(processed, detail=0, paragraph=True)
    return "\n".join(results)


# ─────────────────────────────────────────────────────────────
# MATCH INGREDIENTS
# ─────────────────────────────────────────────────────────────
def match_ingredients(ocr_text):
    text_lower = ocr_text.lower()
    found = []
    seen = set()

    for entry in INGREDIENT_DB:
        for alias in entry["aliases"]:
            if alias.lower() in text_lower:
                if entry["name"] not in seen:
                    found.append(entry)
                    seen.add(entry["name"])

    fluoride_match = re.search(r"f[^\d]{0,10}(\d+[\.,]?\d*)", text_lower)
    if fluoride_match:
        value = float(fluoride_match.group(1).replace(",", "."))
        if value > 1.5 and "Fluoride (F⁻)" not in seen:
            for item in INGREDIENT_DB:
                if item["name"] == "Fluoride (F⁻)":
                    found.append(item)

    ph_match = re.search(r"ph\s*(\d+[\.,]?\d*)", text_lower)
    if ph_match:
        value = float(ph_match.group(1).replace(",", "."))
        if value >= 8.5 and "High pH / Very Alkaline" not in seen:
            for item in INGREDIENT_DB:
                if item["name"] == "High pH / Very Alkaline":
                    found.append(item)

    return found


# ─────────────────────────────────────────────────────────────
# SCORE
# ─────────────────────────────────────────────────────────────
def overall_score(ingredients):
    if not ingredients:
        return 70
    danger = sum(1 for i in ingredients if i["risk_level"] == "DANGER")
    warning = sum(1 for i in ingredients if i["risk_level"] == "WARNING")
    return max(0, min(100, 100 - danger * 25 - warning * 10))


def score_color(score):
    if score >= 70:
        return "#3cdc78"
    elif score >= 40:
        return "#ffb400"
    return "#ff6b6b"


# ─────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────
st.title("🔬 IngredientIQ")
st.write("Upload a product label and analyse ingredients.")

uploaded_file = st.file_uploader("Upload image", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("Analyse Ingredients"):
        with st.spinner("Reading label..."):
            ocr_text = run_ocr(image)

        st.subheader("Extracted Text")
        st.text_area("", ocr_text, height=250)

        matched = match_ingredients(ocr_text)
        score = overall_score(matched)
        color = score_color(score)

        st.markdown(
            f"<h1 style='color:{color};'>{score}/100</h1>",
            unsafe_allow_html=True
        )

        if matched:
            st.subheader("Detected Ingredients")
            for item in matched:
                if item["risk_level"] == "DANGER":
                    st.error(f"{item['name']}\n\n{item['reason']}")
                elif item["risk_level"] == "WARNING":
                    st.warning(f"{item['name']}\n\n{item['reason']}")
                else:
                    st.success(f"{item['name']}\n\n{item['reason']}")
        else:
            st.info("No known ingredients detected.")
