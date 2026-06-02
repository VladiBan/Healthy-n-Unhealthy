import streamlit as st
import easyocr
from PIL import Image, ImageEnhance
import numpy as np
import re

# ---------------------------------------------------
# Настройки на страницата
# ---------------------------------------------------
st.set_page_config(
    page_title="Food Label Scanner",
    page_icon="🧾",
    layout="centered"
)

st.title("🧾 AI Food Label Scanner")
st.write("Разпознаване на вредни съставки от етикети с EasyOCR")

# ---------------------------------------------------
# Списък с вредни съставки
# ---------------------------------------------------
harmful_ingredients = {
    "e621": "MSG / Мононатриев глутамат",
    "палмово масло": "Palm Oil",
    "palm oil": "Palm Oil",
    "аспартам": "Aspartame",
    "aspartame": "Aspartame",
    "глюкозо-фруктозен сироп": "Glucose-Fructose Syrup",
    "glucose-fructose syrup": "Glucose-Fructose Syrup",
    "sodium nitrate": "Sodium Nitrate",
    "msg": "MSG",
    "artificial flavors": "Artificial Flavors",
    "preservatives": "Preservatives"
}

# ---------------------------------------------------
# Зареждане на OCR модела
# ---------------------------------------------------
@st.cache_resource
def load_reader():
    return easyocr.Reader(['bg', 'en'])

reader = load_reader()

# ---------------------------------------------------
# Подобряване на изображението
# ---------------------------------------------------
def preprocess_image(image):
    image = image.convert("RGB")

    # Подобряване на контраста
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)

    return image

# ---------------------------------------------------
# OCR разпознаване
# ---------------------------------------------------
def extract_text(image):
    image_np = np.array(image)

    results = reader.readtext(image_np)

    extracted_text = ""
    confidence_scores = []

    for result in results:
        text = result[1]
        confidence = result[2]

        extracted_text += text + " "
        confidence_scores.append(confidence)

    avg_confidence = (
        sum(confidence_scores) / len(confidence_scores)
        if confidence_scores else 0
    )

    return extracted_text.strip(), avg_confidence

# ---------------------------------------------------
# Търсене на вредни съставки
# ---------------------------------------------------
def detect_harmful_ingredients(text):
    found = []

    text_lower = text.lower()

    for ingredient in harmful_ingredients:
        if ingredient in text_lower:
            found.append(harmful_ingredients[ingredient])

    return list(set(found))

# ---------------------------------------------------
# UI - Качване на снимка
# ---------------------------------------------------
st.subheader("📤 Качи снимка")

uploaded_file = st.file_uploader(
    "Избери изображение",
    type=["jpg", "jpeg", "png"]
)

# ---------------------------------------------------
# UI - Камера
# ---------------------------------------------------
st.subheader("📸 Или направи снимка")

camera_image = st.camera_input("Направи снимка")

image = None

if uploaded_file is not None:
    image = Image.open(uploaded_file)

elif camera_image is not None:
    image = Image.open(camera_image)

# ---------------------------------------------------
# Обработка
# ---------------------------------------------------
if image is not None:

    st.image(image, caption="Качено изображение", use_container_width=True)

    with st.spinner("🔍 Анализиране на етикета..."):

        processed_image = preprocess_image(image)

        extracted_text, confidence = extract_text(processed_image)

        harmful_found = detect_harmful_ingredients(extracted_text)

    # ---------------------------------------------------
    # OCR резултат
    # ---------------------------------------------------
    st.subheader("📝 Разпознат текст")

    if extracted_text:
        st.text_area(
            "OCR Text",
            extracted_text,
            height=200
        )
    else:
        st.warning("Не е открит текст.")

    # ---------------------------------------------------
    # Confidence Score
    # ---------------------------------------------------
    st.subheader("🎯 OCR Confidence")

    st.progress(min(float(confidence), 1.0))

    st.write(f"Средна точност: {confidence:.2%}")

    # ---------------------------------------------------
    # Анализ на съставките
    # ---------------------------------------------------
    st.subheader("⚠️ Анализ на съставките")

    if harmful_found:

        st.error("Открити са потенциално вредни съставки!")

        for ingredient in harmful_found:
            st.markdown(
                f"<span style='color:red; font-size:18px;'>❌ {ingredient}</span>",
                unsafe_allow_html=True
            )

    else:
        st.success("✅ Не са открити вредни съставки.")

# ---------------------------------------------------
# Footer
# ---------------------------------------------------
st.markdown("---")
st.caption("Powered by Streamlit + EasyOCR")
