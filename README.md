# IngredientIQ 🔬

Snap a photo of any product label → OCR extracts the text → Claude AI tells you exactly which ingredients are harmful and why.

---

## Stack

| Library | Role |
|---|---|
| `streamlit` | Web UI |
| `easyocr` | On-device OCR (reads text from the photo) |
| `Pillow` | Image loading / preprocessing |
| `numpy` | Array conversion for EasyOCR |
| `anthropic` | Claude AI — ingredient risk analysis |

---

## Setup

### 1. Clone / copy the files
```
ingredient_scanner/
├── app.py
├── requirements.txt
└── README.md
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> **First run**: EasyOCR will automatically download its English model (~100 MB). This only happens once.

### 4. Set your Anthropic API key
```bash
# macOS / Linux
export ANTHROPIC_API_KEY="sk-ant-..."

# Windows CMD
set ANTHROPIC_API_KEY=sk-ant-...

# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-..."
```

Or create a `.env` file and load it with `python-dotenv`.

### 5. Run
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## How it works

1. **Upload** a photo of a product label (ingredients side works best).
2. **EasyOCR** reads all text from the image entirely on-device.
3. The extracted text is sent to **Claude** (claude-sonnet-4) which:
   - Identifies every ingredient / additive
   - Rates each as **DANGER**, **WARNING**, or **SAFE**
   - Explains the health concern in plain language
   - Assigns an overall safety score (0–100)
4. Results are displayed as colour-coded cards.

---

## Tips for best results

- Photograph the **ingredients list** directly, not the front of the pack.
- Good lighting, flat surface, no motion blur.
- Higher resolution = better OCR accuracy.
- Works with food, cosmetics, supplements, cleaning products — anything with an ingredients list.

---

## Disclaimer

For informational purposes only. Not medical or dietary advice. Always consult a healthcare professional for personal health decisions.
