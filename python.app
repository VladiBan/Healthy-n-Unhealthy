import streamlit as st
import easyocr
from PIL import Image
import numpy as np

st.title("Food Sticker Ingredient Scanner")

# Simple database of some additives
unhealthy_ingredients = {
     # Artificial Colors
    "E102": "Tartrazine - May cause hyperactivity or sensitivity reactions",
    "E104": "Quinoline Yellow - Artificial dye with controversy",
    "E110": "Sunset Yellow - Artificial color, possible reactions",
    "E122": "Carmoisine - Synthetic dye",
    "E124": "Ponceau 4R - Artificial coloring",
    "E129": "Allura Red - Common in candy, drinks, chips",
    
    # Preservatives
    "E211": "Sodium Benzoate - Common in soft drinks and energy drinks",
    "E202": "Potassium Sorbate - Preservative",
    "E250": "Sodium Nitrite - Common in processed meats",
    "E251": "Sodium Nitrate - Processed meat preservative",

    # Flavor Enhancers
    "E621": "MSG (Monosodium Glutamate)",
    "E627": "Disodium Guanylate",
    "E631": "Disodium Inosinate",
    "monosodium glutamate": "MSG flavor enhancer",

    # Antioxidants / Stabilizers
    "E320": "BHA - Controversial preservative",
    "E321": "BHT - Controversial preservative",

    # Sweeteners
    "aspartame": "Artificial sweetener",
    "sucralose": "Artificial sweetener",
    "acesulfame k": "Artificial sweetener",
    "high fructose corn syrup": "Highly processed sweetener",

    # Oils / Fats
    "palm oil": "Highly processed fat",
    "hydrogenated oil": "May contain trans fats",
    "partially hydrogenated oil": "Trans fat risk",

    # Common snack ingredients
    "maltodextrin": "Highly processed carbohydrate",
    "modified starch": "Ultra-processed additive",
    "corn syrup": "Processed sugar",
    "artificial flavor": "Artificial flavoring",
    "artificial flavours": "Artificial flavoring",
    "artificial colors": "Synthetic color additives",

    # Common in Doritos / flavored chips
    "disodium inosinate": "Flavor enhancer often paired with MSG",
    "disodium guanylate": "Flavor enhancer often paired with MSG",
    "yellow 5": "Artificial food dye",
    "yellow 6": "Artificial food dye",
    "red 40": "Artificial food dye",

    # Common in Monster / energy drinks
    "taurine": "Stimulant commonly in energy drinks",
    "guarana": "Natural stimulant",
    "caffeine": "High stimulant (amount matters)",
    "ginseng": "Stimulating additive",

    # Other processed ingredients
    "sodium phosphate": "Phosphate additive",
    "phosphoric acid": "Common in sodas",
    "propylene glycol": "Food additive/stabilizer"

     # E-numbers (works regardless of language)
    "E102": "Tartrazine / Тартразин - Artificial color",
    "E110": "Sunset Yellow / Жълто залез",
    "E124": "Ponceau 4R / Понсо 4R",
    "E211": "Sodium Benzoate / Натриев бензоат",
    "E250": "Sodium Nitrite / Натриев нитрит",
    "E320": "BHA - Controversial preservative",
    "E321": "BHT - Controversial preservative",
    "E621": "MSG / Мононатриев глутамат",

    # English
    "aspartame": "Artificial sweetener",
    "high fructose corn syrup": "Processed sweetener",
    "palm oil": "Processed fat",
    "hydrogenated oil": "Possible trans fats",
    "maltodextrin": "Highly processed additive",
    "artificial flavor": "Artificial flavoring",
    "caffeine": "Stimulant",
    "taurine": "Energy drink stimulant",
    "guarana": "Stimulant",

    # Bulgarian
    "аспартам": "Изкуствен подсладител",
    "палмово масло": "Силно преработена мазнина",
    "хидрогенирано масло": "Възможни транс мазнини",
    "малтодекстрин": "Силно преработена добавка",
    "изкуствени аромати": "Изкуствени овкусители",
    "изкуствени оцветители": "Синтетични оцветители",
    "кофеин": "Стимулант",
    "таурин": "Стимулант в енергийни напитки",
    "гуарана": "Стимулант",

    # Bulgarian E names sometimes written as words
    "мононатриев глутамат": "MSG flavor enhancer",
    "натриев бензоат": "Preservative",
    "натриев нитрит": "Processed meat preservative"
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
