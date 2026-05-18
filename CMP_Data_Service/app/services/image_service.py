from app.utils.arbic_char import SmartTranslator
import cv2

from ..services.ocr_service import tesseract_text
from ..services.visual_service import detect_visual_elements


def extract_image(file_path: str):

    try:

        # =========================
        # LOAD IMAGE
        # =========================
        image = cv2.imread(file_path)

        if image is None:
            return "", {}, "failed", 0.0

        # =========================
        # OCR
        # =========================
        text = tesseract_text(image)
        text = SmartTranslator.smart_translate(text)

        # =========================
        # VISUAL DETECTION
        # =========================
        visual = detect_visual_elements(image)

        return (
            text,
            {"visual": visual},
            "image",
            0.70
        )

    except Exception as error:

        print(f"Image extraction error: {error}")

        return "", {}, "failed", 0.0