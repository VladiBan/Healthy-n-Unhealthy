import streamlit as st
import easyocr
from PIL import Image
import numpy as np

st.title("Food Sticker Ingredient Scanner")

unhealthy_ingredients = {
    "E102": "Tartrazine / Тартразин - Artificial color",
    "E104": "Quinoline Yellow - Artificial dye",
    "E110": "Sunset Yellow / Жълто залез",
    "E122": "Carmoisine - Synthetic dye",
    "E124": "Ponceau 4R / Понсо 4R",
    "E129": "Allura Red - Artificial dye",
    "E202": "Potassium Sorbate - Preservative",
    "E211": "Sodium Benzoate / Натриев бензоат",
    "E250": "Sodium Nitrite / Натриев нитрит",
    "E251": "Sodium Nitrate - Preservative",
    "E320": "BHA - Controversial preservative",
    "E321": "BHT - Controversial preservative",
    "E621": "MSG / Мононатриев глутамат",
    "aspartame": "Artificial sweetener",
    "sucralose": "Artificial sweetener",
    "high fructose corn syrup": "Processed sweetener",
    "palm oil": "Highly processed fat",
    "maltodextrin": "Highly processed additive",
    "artificial flavor": "Artificial flavoring",
    "red 40": "Artificial food dye",
    "yellow 5": "Artificial food dye",
    "аспартам": "Изкуствен подсладител",
    "палмово масло": "Силно преработена мазнина",
    "мононатриев глутамат": "MSG flavor enhancer",
}

@st.cache_resource
def load_reader():
    return easyocr.Reader(['en', 'bg'])

reader = load_reader()

uploaded_file = st.file_uploader("Upload food label image", type=["png", "jpg", "jpeg"])

if uploaded_file:

    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Label", use_container_width=True)

    img_array = np.array(image)

    st.write("Reading ingredients...")

    result = reader.readtext(img_array)

    extracted_text = " ".join([item[1] for item in result])

    st.subheader("Detected Text")
    st.write(extracted_text)

    found_bad = []

    text_lower = extracted_text.lower()
    text_upper = extracted_text.upper()

    for ingredient, warning in unhealthy_ingredients.items():

        if ingredient.startswith("E"):
            if ingredient in text_upper:
                found_bad.append((ingredient, warning))
        else:
            if ingredient in text_lower:
                found_bad.append((ingredient, warning))

    st.subheader("Potentially Concerning Ingredients Found")

    if found_bad:
        for ingredient, warning in found_bad:
            st.error(f"{ingredient}: {warning}")
    else:
        st.success("No flagged ingredients detected.")
