import cv2
import numpy as np


# =========================
# REGION DETECTION
# =========================
def get_candidate_regions(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    regions = []
    H, W = gray.shape[:2]

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h

        if area < 1500 or area > (H * W * 0.2):
            continue

        aspect = w / float(h)

        if aspect > 10 or aspect < 0.1:
            continue

        regions.append((x, y, w, h))

    return regions


# =========================
# CORE LOGIC (SHARED)
# =========================
def _detect_from_image(img):
    if img is None:
        return {
            "logo": False,
            "stamp": False,
            "signature": False,
            "regions": []
        }

    regions = get_candidate_regions(img)

    # 🔥 LIMIT regions
    regions = sorted(regions, key=lambda x: x[2]*x[3], reverse=True)[:5]

    result = {
        "logo": False,
        "stamp": False,
        "signature": False,
        "regions": []
    }

    for (x, y, w, h) in regions:
        crop = img[y:y+h, x:x+w]

        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        edge_density = np.sum(edges) / (w * h)

        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

        blue_mask = cv2.inRange(
            hsv,
            np.array([90, 50, 50]),
            np.array([140, 255, 255])
        )

        blue_ratio = np.sum(blue_mask > 0) / (w * h)

        label = "unknown"
        score = 0

        if blue_ratio > 0.05 and 0.02 < edge_density < 0.2:
            label = "stamp"
            result["stamp"] = True
            score = blue_ratio

        elif 0.01 < edge_density < 0.08 and w > h:
            label = "signature"
            result["signature"] = True
            score = edge_density

        elif edge_density > 0.15 and h < 300:
            label = "logo"
            result["logo"] = True
            score = edge_density

        if label != "unknown":
            result["regions"].append({
                "bbox": [int(x), int(y), int(w), int(h)],
                "label": label,
                "score": round(score, 3)
            })

    return result


# =========================
# PUBLIC FUNCTION (SMART)
# =========================
def detect_visual_elements(input_data):
    """
    Supports both:
    - file path (str)
    - image (numpy array)
    """

    # 🔥 CASE 1: file path
    if isinstance(input_data, str):
        img = cv2.imread(input_data)

    # 🔥 CASE 2: numpy image
    elif isinstance(input_data, np.ndarray):
        img = input_data

    else:
        return {
            "logo": False,
            "stamp": False,
            "signature": False,
            "regions": []
        }

    return _detect_from_image(img)