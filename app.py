import streamlit as st
import easyocr
import numpy as np
import re

from PIL import Image
from PIL import ImageEnhance
from PIL import ImageFilter

# --------------------------------------------------
# PAGE
# --------------------------------------------------

st.set_page_config(
    page_title="Скенер за добавки",
    page_icon="⚠️",
    layout="centered"
)

st.title("⚠️ Скенер за вредни добавки")
st.write("Качи снимка на етикет и приложението ще анализира съставките.")

# --------------------------------------------------
# OCR
# --------------------------------------------------

@st.cache_resource
def load_reader():
    return easyocr.Reader(
        ['bg', 'en'],
        gpu=False
    )

# --------------------------------------------------
# IMAGE PREPROCESSING
# --------------------------------------------------

def preprocess_image(image):

    image = image.convert("RGB")

    image = ImageEnhance.Contrast(image).enhance(3)

    image = ImageEnhance.Sharpness(image).enhance(2)

    image = image.filter(ImageFilter.SHARPEN)

    return image

# --------------------------------------------------
# OCR FIXES
# --------------------------------------------------

def fix_common_ocr_errors(text):

    text = text.upper()

    replacements = {
        "МECO": "МЕСО",
        "МEC0": "МЕСО",
        "CBИНСКО": "СВИНСКО",
        "ГOBEЖДO": "ГОВЕЖДО",
        "ЛAKTOЗA": "ЛАКТОЗА",
        "ГЛУTEN": "ГЛУТЕН",
        "KOHCEPBAHT": "КОНСЕРВАНТ",
        "ACKOPБИHOBA": "АСКОРБИНОВА",
        "KИCEЛИHA": "КИСЕЛИНА",
    }

    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)

    text = re.sub(r"\s+", " ", text)

    return text.strip()

# --------------------------------------------------
# OCR
# --------------------------------------------------

def extract_text(image):

    reader = load_reader()

    img = np.array(image)

    results = reader.readtext(
        img,
        paragraph=True,
        detail=0
    )

    text = " ".join(results)

    text = fix_common_ocr_errors(text)

    return text

# --------------------------------------------------
# E NUMBER NORMALIZATION
# --------------------------------------------------

def normalize_e_numbers(text):

    text = text.upper()

    text = text.replace("Е", "E")

    text = re.sub(
        r"E\s*([0-9]{3,4})",
        r"E\1",
        text
    )

    return text

# --------------------------------------------------
# DATABASE
# --------------------------------------------------

harmful = {

    "E102": "Тартразин (оцветител)",
    "E104": "Оцветител",
    "E110": "Sunset Yellow",
    "E122": "Оцветител",
    "E123": "Оцветител",
    "E124": "Оцветител",
    "E127": "Оцветител",
    "E129": "Оцветител",
    "E131": "Оцветител",
    "E133": "Оцветител",
    "E151": "Оцветител",

    "E211": "Натриев бензоат",
    "E220": "Сулфити",
    "E221": "Консервант",
    "E222": "Консервант",
    "E223": "Консервант",
    "E224": "Консервант",
    "E225": "Консервант",
    "E226": "Консервант",
    "E227": "Консервант",
    "E228": "Консервант",

    "E250": "Натриев нитрит",
    "E251": "Натриев нитрат",
    "E252": "Калиев нитрат",

    "E320": "BHA",
    "E321": "BHT",

    "E407": "Карагенан",
    "E410": "Стабилизатор",
    "E412": "Стабилизатор",
    "E415": "Ксантанова гума",
    "E450": "Фосфати",

    "E621": "Мононатриев глутамат",
    "E627": "Овкусител",
    "E631": "Овкусител",
    "E635": "Овкусител",

    "E950": "Ацесулфам К",
    "E951": "Аспартам",
    "E952": "Подсладител",
    "E954": "Захарин",
    "E955": "Сукралоза",
}

# --------------------------------------------------
# FIND ADDITIVES
# --------------------------------------------------

def find_additives(text):

    text = normalize_e_numbers(text)

    found = []

    for e_code, description in harmful.items():

        if e_code in text:
            found.append((e_code, description))

    return found

# --------------------------------------------------
# FIND INGREDIENTS
# --------------------------------------------------

def find_ingredients(text):

    ingredients = []

    keywords = [
        "СВИНСКО МЕСО",
        "ГОВЕЖДО МЕСО",
        "ДЕКСТРОЗА",
        "ЗАХАР",
        "СОЛ",
        "ПОДПРАВКИ",
        "ЛАКТОЗА",
        "ГЛУТЕН",
        "АСКОРБИНОВА КИСЕЛИНА"
    ]

    for item in keywords:
        if item in text:
            ingredients.append(item)

    return ingredients

# --------------------------------------------------
# UPLOAD
# --------------------------------------------------

uploaded = st.file_uploader(
    "Качи снимка",
    type=["jpg", "jpeg", "png"]
)

# --------------------------------------------------
# MAIN
# --------------------------------------------------

if uploaded:

    image = Image.open(uploaded)

    st.image(
        image,
        caption="Качена снимка",
        use_container_width=True
    )

    processed = preprocess_image(image)

    with st.spinner("Сканиране..."):

        text = extract_text(processed)

        additives = find_additives(text)

        ingredients = find_ingredients(text)

    st.subheader("Разпознат текст")

    st.text_area(
        "",
        text,
        height=250
    )

    st.subheader("Открити съставки")

    if ingredients:

        for item in ingredients:
            st.success(f"✅ {item}")

    else:
        st.info("Не са открити известни съставки.")

    st.subheader("Открити добавки")

    if additives:

        st.error("Открити са добавки:")

        for code, desc in additives:
            st.warning(f"{code} → {desc}")

    else:
        st.success("Не са открити E-добавки от базата.")

    st.subheader("Обобщение")

    if additives:
        st.warning(
            f"Продуктът съдържа {len(additives)} добавки от наблюдавания списък."
        )
    else:
        st.success(
            "Не са открити добавки от наблюдавания списък."
        )
