# from turtle import pd
import re

from app.utils.arbic_char import SmartTranslator
import fitz
import cv2
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor

from ..services.ocr_service import paddle_text, tesseract_text
from ..services.visual_service import detect_visual_elements
import pandas as pd
from deep_translator import GoogleTranslator


# =========================
# SCANNED DETECTION
# =========================
def is_scanned(page):
    text = page.get_text().strip()  
    #  simple page, extract text easily
    images = page.get_images(full=True)

    #  improved logic
    if len(text) < 20 and len(images) > 0:
        return True

    if len(text) > 100:
        return False

    return len(text) < 30


def process_page(page):
    try:
        scanned = is_scanned(page)

        #  if digital → no image rendering needed
        if not scanned:
            text_layer = page.get_text()

            # only run OCR if weak text
            if len(text_layer) > 100:
                return text_layer, {}

        #  render only when needed
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

        if pix.n == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # =========================
        # OCR
        # =========================

        if scanned:
            text = paddle_text(img)
            print("texttttttttttttttttttttttttttttttttttttttttttttttttttttt", len(text))
            # text = SmartTranslator.smart_translate(text)
        else:
            ocr_text = paddle_text(img)
            text_layer = page.get_text()
            text = ocr_text if len(ocr_text) > len(text_layer) else text_layer

        # =========================
        # VISUAL DETECTION
        # =========================
        visual = detect_visual_elements(img)

        return text, visual

    except Exception as e:
        print("Page error:", e)
        return "", {}


# =========================
# HELPER (NO FILE I/O)
# =========================


# =========================
# EXTRACT PDF (PARALLEL)
# =========================
def extract_pdf(file_path):
    try:
        
        doc = fitz.open(file_path)
    except Exception as e:
        print("PDF open error:", e)
        return "", {}, "failed", 0.0

    texts = []
    visuals = {
        "logo": False,
        "stamp": False,
        "signature": False,
        "regions": []
    }

    #  PARALLEL EXECUTION
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(process_page, doc))

    for text, vis in results:
        # print("lenght of text ", text)
      
        texts.append(text)

        # merge visual results
        for k in ["logo", "stamp", "signature"]:
            visuals[k] = visuals[k] or vis.get(k, False)

        visuals["regions"].extend(vis.get("regions", []))

    doc.close()

    return "\n".join(texts), {"visual": visuals}, "pdf", 0.85

def normalize_column(text):
    """
    Convert:
    Chemical name in English
    ->
    chemical_name_in_english
    """

    text = str(text).lower().strip()

    text = re.sub(r'[^a-z0-9]+', '_', text)

    return text.strip('_')


def update_column_names(df):

    # =========================
    # CLEAN COLUMN NAMES
    # =========================
    df.columns = [str(col).strip() for col in df.columns]

    translated_columns = {}

    # =========================
    # TRANSLATE + NORMALIZE
    # =========================
    for col in df.columns:

        try:

            translated = GoogleTranslator(
                source='auto',
                target='en'
            ).translate(col)

            normalized = normalize_column(translated)

            translated_columns[col] = normalized

        except Exception as e:

            print("Translation error:", e)

            translated_columns[col] = normalize_column(col)

    # =========================
    # RENAME COLUMNS
    # =========================
    df.rename(columns=translated_columns, inplace=True)

    return df


def extract_excel(file_path):

    df = None

    # =========================
    # READ FILE
    # =========================
    if file_path.lower().endswith(".csv"):
        df = pd.read_csv(file_path, header=4)

    elif file_path.lower().endswith((".xlsx", ".xls", ".excel")):
        df = pd.read_excel(file_path, header=4)

    else:
        return "Invalid file format", {}, "unknown", 0.0

    # =========================
    # CLEAN COLUMN NAMES
    # =========================
    # df.columns = [str(col).strip() for col in df.columns]
    # print("Excel columns 0:", df.columns)
    
    df = update_column_names(df)

    # print("Excel columns:", df.columns)

    # =========================
    # REMOVE EMPTY ROWS
    # =========================
    df = df.dropna(how="all")
    # print("Non-empty rows:", len(df))

    # =========================
    # FIND HS CODE COLUMN
    # =========================
    hs_col = None

    possible_hs_columns = [
        "hs_code",
        "hs_codes",
        "hs_cods",
        "hscode",
        "hscodes",
        "hscods"
    ]

    for col in df.columns:

        clean_col = (
            col.lower()
            .replace(" ", "")
            .replace("_", "")
        )

        normalized_possible = [
            c.replace("_", "")
            for c in possible_hs_columns
        ]

        if clean_col in normalized_possible:
            hs_col = col
            break

    # print("Detected HS column:", hs_col)

    # =========================
    # CONVERT EXCEL DATA
    # ARRAY OF OBJECTS
    # =========================
    records = []

    for _, row in df.iterrows():

        item = {}

        for col in df.columns:

            value = row[col]

            if pd.isna(value):
                value = ""

            value = str(value).strip()

            item[col] = value

        # =========================
        # HS CODE EXTRACTION
        # =========================
        if hs_col:

            hs_value = item.get(hs_col, "")

            item["fullHscode"] = hs_value
            item["4DigitHscode"] = hs_value[:4]
            item["6DigitHScode"] = hs_value.replace(".", "")

        records.append(item)

    # print(records[:1])

    return records, {}, "excel", 0.9
