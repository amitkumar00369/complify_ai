# import re

# def extract_clauses(text):
#     if not text:
#         return []

#     text = text.lower()
#     clauses = []

#     # 🔹 Regulation
#     if "machinery safety" in text:
#         clauses.append({
#             "type": "Regulation",
#             "value": "Machinery Safety",
#             "confidence": 0.9
#         })

#     # 🔹 Standard
#     std = re.findall(r"(en\s*\d{4,5}[-–]?\d*)", text)
#     if std:
#         clauses.append({
#             "type": "Standard",
#             "value": std[0],
#             "confidence": 0.95
#         })

#     # 🔹 Certificate
#     if "certificate of conformity" in text or "coc" in text:
#         clauses.append({
#             "type": "Certification",
#             "value": "COC",
#             "confidence": 0.9
#         })

#     # 🔹 Test report
#     if "test report" in text or "report number" in text:
#         clauses.append({
#             "type": "Test Report",
#             "value": True,
#             "confidence": 0.85
#         })

#     # 🔹 Product
#     if "product name" in text:
#         clauses.append({
#             "type": "Product Identification",
#             "confidence": 0.9
#         })

#     return clauses

import re


def extract_clauses(text):

    if not text:
        return []

    text_lower = text.lower()

    clauses = []

    # =====================================================
    # TECHNICAL REGULATION
    # =====================================================

    tr_matches = re.findall(

        r"(technical regulation for [a-zA-Z0-9\s\-\(\)&]+)",

        text_lower
    )

    for tr in tr_matches:

        tr = tr.strip()

        # remove unwanted continuation
        stop_words = [
            "manufacturer",
            "product",
            "report",
            "country",
            "address"
        ]

        for stop in stop_words:

            if stop in tr:

                tr = tr.split(stop)[0].strip()

        clauses.append({

            "type": "Technical Regulation",

            "value": tr.title(),

            "confidence": 0.90
        })

    # =====================================================
    # STANDARD
    # =====================================================

    standards = re.findall(

        r"(iec\s*\d+(?:[-–]\d+)*)|"
        r"(en\s*\d+(?:[-–]\d+)*)|"
        r"(iso\s*\d+(?:[-–]\d+)*)|"
        r"(saso\s*gso\s*\d+(?::\d+)?)",

        text_lower
    )

    for std in standards:

        std_value = next(
            (s for s in std if s),
            None
        )

        if std_value:

            clauses.append({

                "type": "Standard",

                "value": std_value.upper(),

                "confidence": 0.95
            })

    # =====================================================
    # CERTIFICATION
    # =====================================================

    if (
        "certificate of conformity" in text_lower
        or "coc" in text_lower
        or "pcoc" in text_lower
    ):

        clauses.append({

            "type": "Certification",

            "value": "COC",

            "confidence": 0.90
        })

    # =====================================================
    # TEST REPORT
    # =====================================================

    if (
        "test report" in text_lower
        or "report number" in text_lower
        or "cb report" in text_lower
    ):

        clauses.append({

            "type": "Test Report",

            "value": True,

            "confidence": 0.85
        })

    # =====================================================
    # PRODUCT IDENTIFICATION
    # =====================================================

    if (
        "product name" in text_lower
        or "model type" in text_lower
        or "product description" in text_lower
    ):

        clauses.append({

            "type": "Product Identification",

            "confidence": 0.90
        })

    # =====================================================
    # HS CODE
    # =====================================================

    hs_match = re.search(

        r"hs\s*code\s*(\d{4,12})",

        text_lower
    )

    if hs_match:

        clauses.append({

            "type": "HS Code",

            "value": hs_match.group(1),

            "confidence": 0.95
        })

    # =====================================================
    # COUNTRY OF ORIGIN
    # =====================================================

    country_match = re.search(

        r"country of origin\s*([a-zA-Z\s]+)",

        text_lower
    )

    if country_match:

        country = country_match.group(1).strip()

        country = country.split("hs code")[0].strip()

        clauses.append({

            "type": "Country Of Origin",

            "value": country.title(),

            "confidence": 0.88
        })

    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    unique = []

    seen = set()

    for clause in clauses:

        key = (
            clause.get("type"),
            clause.get("value")
        )

        if key not in seen:

            seen.add(key)

            unique.append(clause)

    return unique