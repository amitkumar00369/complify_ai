# import re
# from collections import defaultdict


# def extract_standard_intelligence(text: str):
#     """
#     Convert raw IEC/ISO/EN standard text into structured compliance intelligence
#     """

#     result = {
#         "standard_code": None,
#         "title": None,
#         "scope": None,
#         "normative_references": [],
#         "terms": [],
#         "requirements": [],
#         "tests": [],
#         "tables": [],
#         "clauses": []
#     }

#     text = text.replace("\n", " ")
#     text = re.sub(r"\s+", " ", text)

#     # =====================================================
#     # 1. STANDARD CODE
#     # =====================================================
#     std_match = re.search(r"(IEC\s?\d{4,5}(?:-\d+)?)", text, re.I)

#     if std_match:
#         result["standard_code"] = std_match.group(1).upper()

#     # =====================================================
#     # 2. TITLE
#     # =====================================================
#     title_match = re.search(
#         r"IEC\s?\d{4,5}(?:-\d+)?[: ]\d{4}.*?([A-Z].*?single cells)",
#         text,
#         re.I
#     )

#     if title_match:
#         result["title"] = title_match.group(1).strip()

#     # =====================================================
#     # 3. SCOPE
#     # =====================================================
#     scope_match = re.search(
#         r"1 Scope(.*?)2 Normative references",
#         text,
#         re.I
#     )

#     if scope_match:
#         result["scope"] = scope_match.group(1).strip()

#     # =====================================================
#     # 4. NORMATIVE REFERENCES
#     # =====================================================
#     refs = re.findall(
#         r"(IEC\s\d{4,5}(?:-\d+)?)",
#         text
#     )

#     unique_refs = list(set(refs))

#     result["normative_references"] = [
#         {"standard": ref}
#         for ref in unique_refs
#         if ref != result["standard_code"]
#     ]

#     # =====================================================
#     # 5. TERMS & DEFINITIONS
#     # =====================================================
#     terms_section = re.search(
#         r"3 Terms and definitions(.*?)4 Parameter measurement tolerances",
#         text,
#         re.I
#     )

#     if terms_section:
#         terms_text = terms_section.group(1)

#         term_matches = re.findall(
#             r"(\d+\.\d+)\s+([a-zA-Z\s\-]+)\s+(.*?) (?=\d+\.\d+|4 Parameter)",
#             terms_text,
#             re.S
#         )

#         for clause, term, definition in term_matches:
#             result["terms"].append({
#                 "clause": clause,
#                 "term": term.strip(),
#                 "definition": definition.strip()
#             })

#     # =====================================================
#     # 6. REQUIREMENTS (shall / must)
#     # =====================================================
#     requirement_matches = re.findall(
#         r"([^\.]*\b(?:shall|must|required)\b[^\.]*\.)",
#         text,
#         re.I
#     )

#     for req in requirement_matches:
#         result["requirements"].append({
#             "requirement": req.strip(),
#             "severity": "mandatory"
#         })

#     # =====================================================
#     # 7. TEST SECTIONS
#     # =====================================================
#     test_matches = re.findall(
#         r"(\d+\.\d+(?:\.\d+)?)\s+([A-Z][A-Za-z\s\-]+test.*?) (?=\d+\.\d+|\Z)",
#         text,
#         re.S
#     )

#     for clause, title in test_matches:
#         result["tests"].append({
#             "clause": clause,
#             "title": title.strip()
#         })

#     # =====================================================
#     # 8. TABLE REFERENCES
#     # =====================================================
#     tables = re.findall(
#         r"(Table\s\d+\s[–-]\s.*?)(?=Table\s\d+|\Z)",
#         text,
#         re.S
#     )

#     for table in tables:
#         result["tables"].append({
#             "table_name": table.strip()[:200]
#         })

#     # =====================================================
#     # 9. CLAUSE EXTRACTION
#     # =====================================================
#     clause_matches = re.findall(
#         r"(\d+(?:\.\d+)*)\s+([A-Z][A-Za-z\s\-]+)",
#         text
#     )

#     added = set()

#     for clause_num, title in clause_matches:

#         key = f"{clause_num}_{title}"

#         if key in added:
#             continue

#         added.add(key)

#         result["clauses"].append({
#             "standard": result["standard_code"],
#             "clause": clause_num,
#             "title": title.strip(),
#             "severity": "mandatory"
#         })

#     return result

import re
from typing import List, Dict, Any


# =========================================================
# MAIN KNOWLEDGE OBJECT ENGINE
# =========================================================

def build_knowledge_objects(text: str) -> Dict[str, Any]:

    text = normalize_text(text)

    return {
        "metadata": extract_metadata(text),
        "scope": extract_scope(text),
        "references": extract_references(text),
        "definitions": extract_definitions(text),
        "requirements": extract_requirements(text),
        "limits": extract_limits(text),
        "tests": extract_tests(text),
        "labeling": extract_labeling(text),
        "clauses": extract_clauses(text)
    }


# =========================================================
# NORMALIZE
# =========================================================

def normalize_text(text: str) -> str:
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# =========================================================
# METADATA
# =========================================================

def extract_metadata(text: str) -> Dict[str, Any]:

    metadata = {
        "standard_code": None,
        "year": None,
        "title": None
    }

    std_match = re.search(
        r"(GSO|IEC|ISO|GB/T|EN)\s*[\d\/\-]+",
        text,
        re.I
    )

    if std_match:
        metadata["standard_code"] = std_match.group(0)

    year_match = re.search(r"(20\d{2})", text)

    if year_match:
        metadata["year"] = year_match.group(1)

    title_match = re.search(
        r"(Safety Requirements.*?Products)",
        text,
        re.I
    )

    if title_match:
        metadata["title"] = title_match.group(1)

    return metadata


# =========================================================
# SCOPE
# =========================================================

def extract_scope(text: str) -> Dict[str, Any]:

    scope = {
        "section": "1",
        "content": None
    }

    match = re.search(
        r"1\.\s*SCOPE(.*?)2\.\s*NORMATIVE REFERENCES",
        text,
        re.I
    )

    if match:
        scope["content"] = match.group(1).strip()

    return scope


# =========================================================
# REFERENCES
# =========================================================

def extract_references(text: str) -> List[Dict]:

    refs = re.findall(
        r"(GSO ISO\s*\d+|IEC\s*\d+|ISO\s*\d+|GB/T\s*\d+)",
        text
    )

    unique_refs = list(set(refs))

    return [
        {
            "standard": ref,
            "type": "reference_standard"
        }
        for ref in unique_refs
    ]


# =========================================================
# DEFINITIONS
# =========================================================

def extract_definitions(text: str) -> List[Dict]:

    definitions = []

    matches = re.findall(
        r"(\d+\.\d+)\s+([A-Za-z\s\-]+)\s+(.*?)(?=\d+\.\d+|\Z)",
        text,
        re.S
    )

    for clause, term, definition in matches:

        if len(term.strip()) < 3:
            continue

        definitions.append({
            "clause": clause,
            "term": term.strip(),
            "definition": definition.strip()[:1000]
        })

    return definitions


# =========================================================
# REQUIREMENTS
# =========================================================

def extract_requirements(text: str) -> List[Dict]:

    requirements = []

    reqs = re.findall(
        r"([^\.]*(?:shall|must|required|should not)[^\.]*\.)",
        text,
        re.I
    )

    for req in reqs:

        severity = "mandatory"

        if "should" in req.lower():
            severity = "recommended"

        requirements.append({
            "requirement": req.strip(),
            "severity": severity,
            "type": "compliance_requirement"
        })

    return requirements


# =========================================================
# LIMITS
# =========================================================

def extract_limits(text: str) -> List[Dict]:

    limits = []

    patterns = [
        r"(Lead)\s*:\s*(\d+\s*ppm)",
        r"(Mercury)\s*:\s*(\d+\s*ppm)",
        r"(Cadmium)\s*:\s*(\d+\s*ppm)",
        r"(Arsenic)\s*:\s*(\d+\s*ppm)",
        r"(Antimony)\s*:\s*(\d+\s*ppm)"
    ]

    for pattern in patterns:

        matches = re.findall(pattern, text, re.I)

        for parameter, value in matches:

            limits.append({
                "parameter": parameter,
                "max_limit": value,
                "type": "safety_limit"
            })

    return limits


# =========================================================
# TESTS
# =========================================================

def extract_tests(text: str) -> List[Dict]:

    tests = []

    test_matches = re.findall(
        r"(test method|microbiology|protection factor|SPF|UVA)",
        text,
        re.I
    )

    for test in set(test_matches):

        tests.append({
            "test_name": test,
            "type": "compliance_test"
        })

    return tests


# =========================================================
# LABELING
# =========================================================

def extract_labeling(text: str) -> List[Dict]:

    labels = []

    label_keywords = [
        "country of origin",
        "manufacturer",
        "nominal content",
        "batch number",
        "expiry date"
    ]

    for keyword in label_keywords:

        if keyword.lower() in text.lower():

            labels.append({
                "requirement": keyword,
                "type": "labeling_requirement"
            })

    return labels


# =========================================================
# CLAUSES
# =========================================================

def extract_clauses(text: str) -> List[Dict]:

    clauses = []

    clause_matches = re.findall(
        r"\b(\d+(?:\.\d+)+)\b",
        text
    )

    unique_clauses = sorted(set(clause_matches))

    for clause in unique_clauses:

        clauses.append({
            "clause": clause,
            "severity": "mandatory",
            "type": "clause"
        })

    return clauses