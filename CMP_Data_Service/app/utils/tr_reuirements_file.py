import re
def extract_article_content(article_no, text):

    start_pattern = rf'Article\s*\(\s*{article_no}\s*\)'
    end_pattern = rf'Article\s*\(\s*{article_no + 1}\s*\)'

    start_match = re.search(start_pattern, text, re.I)

    if not start_match:
        return ""

    content = text[start_match.end():]

    end_match = re.search(end_pattern, content, re.I)

    if end_match:
        content = content[:end_match.start()]

    return content.strip()
def classify_section(title: str) -> dict:

    title = re.sub(r"\s+", " ", title).strip().lower()

    if "preamble" in title:
        return {
            "type": "preamble",
            "should_process": False
        }

    if any(
        keyword in title
        for keyword in [
            "definition",
            "definitions",
            "term",
            "terms"
        ]
    ):
        return {
            "type": "definitions",
            "should_process": True
        }

    if any(
        keyword in title
        for keyword in [
            "scope",
            "application"
        ]
    ):
        return {
            "type": "scope",
            "should_process": True
        }

    if any(
        keyword in title
        for keyword in [
            "objective",
            "objectives"
        ]
    ):
        return {
            "type": "objectives",
            "should_process": False
        }

    if any(
        keyword in title
        for keyword in [
            "obligation",
            "obligations",
            "responsibilit",
            "supplier",
            "importer",
            "manufacturer"
        ]
    ):
        return {
            "type": "supplier_obligations",
            "should_process": True
        }

    if any(
        keyword in title
        for keyword in [
            "marking",
            "label",
            "labeling",
            "labelling",
            "packaging"
        ]
    ):
        return {
            "type": "marking",
            "should_process": True
        }

    if any(
        keyword in title
        for keyword in [
            "conformity",
            "assessment",
            "certification",
            "certificate"
        ]
    ):
        return {
            "type": "conformity_assessment",
            "should_process": True
        }

    if any(
        keyword in title
        for keyword in [
            "supply procedure",
            "supply procedures",
            "distribution",
            "import",
            "export"
        ]
    ):
        return {
            "type": "procedures",
            "should_process": True
        }

    if any(
        keyword in title
        for keyword in [
            "annex",
            "appendix",
            "schedule"
        ]
    ):
        return {
            "type": "annex",
            "should_process": True
        }

    if any(
        keyword in title
        for keyword in [
            "violation",
            "violations",
            "penalty",
            "penalties"
        ]
    ):
        return {
            "type": "enforcement",
            "should_process": False
        }

    if any(
        keyword in title
        for keyword in [
            "general provision",
            "transitional",
            "publication"
        ]
    ):
        return {
            "type": "general",
            "should_process": False
        }

    return {
        "type": "other",
        "should_process": False
    }

import re

def normalize_standard(std):

    std = re.sub(
        r'ISOIIEC',
        'ISO/IEC',
        std,
        flags=re.I
    )

    std = re.sub(
        r'ISO\s+IEC',
        'ISO/IEC',
        std,
        flags=re.I
    )

    std = re.sub(
        r'ISO/IEC\s*',
        'ISO/IEC ',
        std,
        flags=re.I
    )

    std = re.sub(
        r'\s+',
        ' ',
        std
    ).strip()

    return std


def extract_requirements(clause_no, clause_text):

    text = re.sub(r"\s+", " ", clause_text).strip()

    requirements = []

    seen = set()

    mandatory = bool(
        re.search(
            r'\b(shall|must|required|mandatory)\b',
            text,
            re.I
        )
    )

    document_patterns = {

        "certificate": [
            r'Certificates?\s+of\s+Conformity',
            r'Certificates?'
        ],

        "declaration": [
            r'Declaration\s+of\s+Conformity'
        ],

        "technical_file": [
            r'Technical\s+File'
        ],

        "risk_assessment": [
            r'Risk\s+Assessment(?:\s+Document)?'
        ],

        "manual": [
            r'User\s+Manual',
            r'Product\s+Manual'
        ],

        "report": [
            r'Test\s+Report',
            r'Inspection\s+Report'
        ],

        "quality_mark": [
            r'Saudi\s+Quality\s+Mark'
        ]
    }

    # ------------------------
    # Extract documents
    # ------------------------

    for req_type, patterns in document_patterns.items():

        for pattern in patterns:

            matches = re.finditer(
                pattern,
                text,
                flags=re.I
            )

            for match in matches:

                name = match.group(0).strip()

                key = (
                    req_type,
                    name.lower()
                )

                if key in seen:
                    continue

                seen.add(key)

                requirements.append(
                    {
                        "clause": clause_no,
                        "requirement_type": req_type,
                        "requirement_name": name,
                        "mandatory": mandatory,
                        "source_text": text
                    }
                )

    # ------------------------
    # Standards
    # ------------------------

    STANDARD_PATTERNS = [

    r'ISO/?IEC\s*\d+(?:[-:]\d+)*',
    r'ISO\s*\d+(?:[-:]\d+)*',
    r'IEC\s*\d+(?:[-:]\d+)*',
    r'EN\s*\d+(?:[-:]\d+)*',
    r'ASTM\s*[A-Z]?\d+(?:[-:]\d+)*',
    r'NFPA\s*\d+(?:[-:]\d+)*',
    r'SASO\s*[-A-Z0-9]+',
    r'GSO\s*\d+(?:[-:]\d+)*',
    r'UL\s*\d+(?:[-:]\d+)*'
]

    seen = set()

    for pattern in STANDARD_PATTERNS:

        matches = re.findall(
            pattern,
            text,
            flags=re.I
        )

        for std in matches:

            std = normalize_standard(std)

            key = (
                "standard",
                std.lower()
            )

            if key in seen:
                continue

            seen.add(key)

            requirements.append({
                "clause": clause_no,
                "requirement_type": "standard",
                "requirement_name": std,
                "mandatory": mandatory,
                "source_text": text
            })

    return requirements
# import re
import re


def extract_clauses(article_text):

    article_text = re.sub(r"\s+", " ", article_text).strip()

    pattern = re.compile(
        r'(\d+/\d+)'
        r'\s+'
        r'(.*?)'
        r'(?=\d+/\d+\s+|$)',
        re.S
    )

    clauses = []

    for match in pattern.finditer(article_text):

        clause_no = (
            match.group(1)
            .replace("/", ".")
        )

        clause_content = match.group(2).strip()

        clauses.append(
            {
                "clause": clause_no,
                "content": clause_content
            }
        )

    return clauses


import re


def normalize_requirements(requirements):

    normalized = []

    seen = set()

    GENERIC_NAMES = {
        "certificate",
        "certificates",
        "report",
        "reports",
        "manual",
        "manuals",
        "document",
        "documents"
    }

    for req in requirements:

        name = req.get(
            "requirement_name",
            ""
        ).strip()

        req_type = req.get(
            "requirement_type",
            ""
        )

        # -------------------------
        # Fix OCR issues
        # -------------------------

        name = re.sub(
            r'ISOIIEC',
            'ISO/IEC',
            name,
            flags=re.I
        )

        name = re.sub(
            r'\s+',
            ' ',
            name
        ).strip()

        # -------------------------
        # Remove generic names
        # -------------------------

        if name.lower() in GENERIC_NAMES:
            continue

        # -------------------------
        # Normalize plurals
        # -------------------------

        if name.lower() == "certificates of conformity":
            name = "Certificate of Conformity"

        if name.lower() == "declarations of conformity":
            name = "Declaration of Conformity"

        if name.lower() == "technical files":
            name = "Technical File"

        # -------------------------
        # Quality Mark is optional
        # -------------------------

        if (
            req_type == "quality_mark"
            and "saudi quality mark" in name.lower()
        ):
            req["mandatory"] = False

        # -------------------------
        # Update cleaned name
        # -------------------------

        req["requirement_name"] = name

        # -------------------------
        # Deduplicate
        # -------------------------

        key = (
            req.get("requirement_type"),
            name.lower()
        )

        if key in seen:
            continue

        seen.add(key)

        normalized.append(req)

    return normalized