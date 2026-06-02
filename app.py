import streamlit as st
import easyocr
import numpy as np
import re
from PIL import Image, ImageEnhance

# ---------------------------
# STREAMLIT UI
# ---------------------------

st.set_page_config(page_title="Скенер за добавки", page_icon="⚠️")

st.title("⚠️ Скенер за вредни добавки")
st.write("Качи снимка или използвай камера.")

# ---------------------------
# OCR READER
# ---------------------------

@st.cache_resource
def load_reader():
    return easyocr.Reader(['bg', 'en'])


# ---------------------------
# IMAGE PREPROCESSING
# ---------------------------

def preprocess_image(image):

    image = image.convert("RGB")

    # increase contrast
    image = ImageEnhance.Contrast(image).enhance(2)

    # sharpen
    image = ImageEnhance.Sharpness(image).enhance(2)

    return image


# ---------------------------
# FIX OCR TEXT (VERY IMPORTANT)
# ---------------------------

def clean_ocr_text(text):

    text = text.upper()

    # OCR fixes
    text = text.replace("G", "E")
    text = text.replace("[", "E")
    text = text.replace("O", "0")

    text = re.sub(r"\s+", " ", text)

    return text


# ---------------------------
# OCR FUNCTION
# ---------------------------

def extract_text(image):

    reader = load_reader()

    img_array = np.array(image)

    results = reader.readtext(img_array)

    text = " ".join([r[1] for r in results])

    return clean_ocr_text(text)


# ---------------------------
# DETECTOR (FIXED + ROBUST)
# ---------------------------

def find_harmful_ingredients(text):

    harmful = {

        # -------------------
        # COLORANTS / ОЦВЕТИТЕЛИ
        # -------------------
        "E102": "Colorant / Оцветител (Tartrazine)",
        "E104": "Colorant / Оцветител",
        "E110": "Colorant / Оцветител (Sunset Yellow)",
        "E122": "Colorant / Оцветител",
        "E123": "Colorant / Оцветител",
        "E124": "Colorant / Оцветител",
        "E127": "Colorant / Оцветител",
        "E129": "Colorant / Оцветител",
        "E131": "Colorant / Оцветител",
        "E133": "Colorant / Оцветител",
        "E151": "Colorant / Оцветител",

        # -------------------
        # PRESERVATIVES / КОНСЕРВАНТИ
        # -------------------
        "E211": "Preservative / Консервант (Sodium benzoate)",
        "E220": "Preservative / Консервант (Sulphites)",
        "E221": "Preservative / Консервант",
        "E222": "Preservative / Консервант",
        "E223": "Preservative / Консервант",
        "E224": "Preservative / Консервант",
        "E225": "Preservative / Консервант",
        "E226": "Preservative / Консервант",
        "E227": "Preservative / Консервант",
        "E228": "Preservative / Консервант",
        "E250": "Preservative / Консервант (Sodium nitrite)",

        # -------------------
        # SWEETENERS / ПОДСЛАДИТЕЛИ
        # -------------------
        "E950": "Sweetener / Подсладител (Acesulfame K)",
        "E951": "Sweetener / Подсладител (Aspartame / Аспартам)",
        "E952": "Sweetener / Подсладител",
        "E954": "Sweetener / Подсладител (Saccharin)",
        "E955": "Sweetener / Подсладител (Sucralose)",

        # -------------------
        # FLAVOR ENHANCERS / ОВКУСИТЕЛИ
        # -------------------
        "E621": "Flavor enhancer / Овкусител (MSG / Monosodium glutamate)",
        "E627": "Flavor enhancer",
        "E631": "Flavor enhancer",
        "E635": "Flavor enhancer",

        # -------------------
        # STABILIZERS / СТАБИЛИЗАТОРИ
        # -------------------
        "E320": "Antioxidant / Антиоксидант (BHA)",
        "E321": "Antioxidant / Антиоксидант (BHT)",
        "E407": "Stabilizer / Стабилизатор (Carrageenan)",
        "E410": "Stabilizer",
        "E412": "Stabilizer",
        "E415": "Stabilizer",
        "E450": "Stabilizer (Phosphates)",

        # -------------------
        # OTHER HARMFUL INGREDIENTS / ДРУГИ
        # -------------------
        "palm oil": "Harmful fat / Палмово масло",
        "палмово масло": "Harmful fat / Palm oil",

        "hydrogenated oil": "Trans fat / Транс мазнини",
        "partially hydrogenated": "Trans fat",

        "high fructose corn syrup": "Sweetener / High fructose syrup",
        "високо фруктозен сироп": "Sweetener",

        "monosodium glutamate": "Flavor enhancer / MSG",
        "мононатриев глутамат": "Flavor enhancer",

        "aspartame": "Sweetener / Аспартам",
        "аспартам": "Sweetener"
    }

    found = []

    text = text.lower()

    for ingredient, category in harmful.items():
        if ingredient.lower() in text:
            found.append((ingredient, category))

    return found

# ---------------------------
# INPUTS
# ---------------------------

uploaded = st.file_uploader("📤 Качи снимка", type=["png", "jpg", "jpeg"])
camera = st.camera_input("📷 Камера")

image = None

if uploaded:
    image = Image.open(uploaded)

elif camera:
    image = Image.open(camera)


# ---------------------------
# MAIN LOGIC
# ---------------------------

if image:

    st.image(image, caption="Снимка", use_container_width=True)

    processed = preprocess_image(image)

    with st.spinner("🔍 Сканиране..."):

        text = extract_text(processed)

        results = find_harmful_ingredients(text)

    st.subheader("📝 Разпознат текст")

    with st.expander("Покажи текста"):
        st.write(text)

    st.subheader("⚠️ Резултати")

    if results:

        st.error("Открити са вредни добавки!")

        for e, name in results:
            st.warning(f"❌ {e} → {name}")

    else:
        st.success("✅ Няма открити вредни добавки")
