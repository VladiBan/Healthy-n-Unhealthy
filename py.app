import streamlit as st
import easyocr
from PIL import Image
import numpy as np

st.title("Food Sticker Ingredient Scanner")

# Simple database of some additives
unhealthy_ingredients = {
    "E102": "Tartrazine - Artificial coloring, may cause hyperactivity",
    "E110": "Sunset Yellow - Artificial dye, possible reactions",
    "E124": "Ponceau 4R - Artificial coloring, controversial",
    "E211": "Sodium Benzoate - Preservative, possible concerns",
    "E250": "Sodium Nitrite - Processed meat preservative",
    "E320": "BHA - Possible carcinogenic concerns",
    "E321": "BHT - Preservative with debated safety",
    "E621": "MSG - Flavor enhancer, some people avoid it",
    "aspartame": "Artificial sweetener",
    "high fructose corn syrup": "Highly processed sweetener",
    "palm oil": "Highly processed fat",
    "monosodium glutamate": "MSG flavor enhancer"
}

reader = easyocr.Reader(['en'])

uploaded_file = st.file_uploader(
    "Upload food label image",
    type=["png", "jpg", "jpeg"]
)

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

    text_upper = extracted_text.upper()
    text_lower = extracted_text.lower()

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
        st.success("No flagged ingredients detected from current database.")
