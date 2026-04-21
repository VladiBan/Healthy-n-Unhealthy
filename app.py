import streamlit as st
from PIL import Image
import pytesseract
import numpy as np

st.title("Food Sticker Ingredient Scanner")

unhealthy_ingredients = {
    "E102": "Tartrazine / Artificial color",
    "E104": "Quinoline Yellow",
    "E110": "Sunset Yellow",
    "E122": "Carmoisine",
    "E124": "Ponceau 4R",
    "E129": "Allura Red",
    "E202": "Potassium Sorbate",
    "E211": "Sodium Benzoate",
    "E250": "Sodium Nitrite",
    "E320": "BHA preservative",
    "E321": "BHT preservative",
    "E621": "MSG flavor enhancer",
    "aspartame": "Artificial sweetener",
    "sucralose": "Artificial sweetener",
    "palm oil": "Processed fat",
    "maltodextrin": "Processed additive",
    "red 40": "Artificial dye",
    "yellow 5": "Artificial dye",
}

uploaded_file = st.file_uploader(
    "Upload food label image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(image, caption="Uploaded Label", use_container_width=True)

    st.write("Reading text...")

    # OCR with Tesseract
    extracted_text = pytesseract.image_to_string(image)

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
