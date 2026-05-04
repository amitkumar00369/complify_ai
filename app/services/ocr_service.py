import cv2
import pytesseract
from paddleocr import PaddleOCR
from ..config.settings import TESSERACT_PATH

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# 🔥 initialize once
paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en')


def paddle_text(img):
    try:
        result = paddle_ocr.ocr(img)
        text = ""

        if result:
            for line in result:
                for word in line:
                    text += word[1][0] + " "

        return text.strip()
    except:
        return ""


def tesseract_text(img):
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return pytesseract.image_to_string(gray, config="--oem 3 --psm 6")
    except:
        return ""