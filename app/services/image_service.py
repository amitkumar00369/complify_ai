from ..services.visual_service import detect_visual_elements

def extract_image(file_path):
    import cv2
    from services.ocr_service import tesseract_text

    img = cv2.imread(file_path)
    text = tesseract_text(img)

    visual = detect_visual_elements(file_path)

    return text, {"visual": visual}, "image", 0.7