import cv2
import pytesseract
from paddleocr import PaddleOCR
from ..config.settings import TESSERACT_PATH
# from langdetect import detect

# text = extracted_text

# language = detect(text)

# print(language)


pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

#  initialize once
paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en') # arebic
    
# ocr_models = {
#     "en": PaddleOCR(use_angle_cls=True, lang="en"),
#     "ar": PaddleOCR(use_angle_cls=True, lang="ar")
# }

def get_ocr_model(language):

    if language == "ar":
        return ocr_models["ar"]

    return ocr_models["en"]
import re

def clean_ocr_text(text):

    if not text:
        return ""

    # remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    # remove repeated garbage chars
    text = re.sub(r'(.)\1{5,}', r'\1', text)

    # fix broken SASO
    text = text.replace("AS0", "SASO")
    text = text.replace("IE0", "IEC")
    text = text.replace("G0", "GSO")

    return text.strip()

def paddle_text(img):

    try:

        result = paddle_ocr.ocr(img)

        if not result:
            return ""

        extracted = []

        # =========================
        # EXTRACT TEXT + POSITION
        # =========================

        for res in result:

            if not res:
                continue

            for line in res:

                try:

                    box = line[0]

                    text = line[1][0].strip()

                    confidence = float(line[1][1])

                    if not text:
                        continue

                    if confidence < 0.60:
                        continue

                    x = int(box[0][0])
                    y = int(box[0][1])

                    extracted.append({
                        "text": text,
                        "x": x,
                        "y": y,
                        "confidence": confidence
                    })

                except Exception as e:

                    print("LINE ERROR:", e)

        # =========================
        # SORT FOR ARABIC RTL
        # =========================

        extracted = sorted(
            extracted,
            key=lambda item: (
                item["y"],
                -item["x"]
            )
        )

        # =========================
        # GROUP INTO LINES
        # =========================

        lines = []

        current_line = []

        current_y = None

        line_threshold = 25

        for item in extracted:

            if current_y is None:

                current_y = item["y"]

            # same visual line
            if abs(item["y"] - current_y) <= line_threshold:

                current_line.append(item)

            else:

                # sort RTL inside line
                current_line = sorted(
                    current_line,
                    key=lambda x: -x["x"]
                )

                line_text = " ".join(
                    [x["text"] for x in current_line]
                )

                lines.append(line_text)

                current_line = [item]

                current_y = item["y"]

        # append last line
        if current_line:

            current_line = sorted(
                current_line,
                key=lambda x: -x["x"]
            )

            line_text = " ".join(
                [x["text"] for x in current_line]
            )

            lines.append(line_text)

        # =========================
        # CLEAN TEXT
        # =========================

        final_text = "\n".join(lines)

        final_text = clean_ocr_text(final_text)

        return final_text

    except Exception as e:

        print("PADDLE OCR ERROR:", e)

        return ""


def tesseract_text(img):
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return pytesseract.image_to_string(gray, config="--oem 3 --psm 6")
    except:
        return ""