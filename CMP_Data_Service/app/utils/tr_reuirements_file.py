import re
def find_article_number(text):
    # text = "Article (6) Conformity Assessment Procedures"

    match = re.search(r"Article\s*\(?(\d+)\)?", text, re.IGNORECASE)

    if match:
        article_no = int(match.group(1))
        return article_no
    return 7
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



def normalize_standard(text):

    text = re.sub(
        r'ISOIIEC',
        'ISO/IEC',
        text,
        flags=re.I
    )

    text = re.sub(
        r'ISO\s+IEC',
        'ISO/IEC',
        text,
        flags=re.I
    )

    text = re.sub(
        r'ISO\/IEC\s*',
        'ISO/IEC ',
        text,
        flags=re.I
    )

    text = re.sub(
        r'\s+',
        ' ',
        text
    )

    return text.strip()


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
            r'certificate\s+of\s+conformity'
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

        "test_report": [
            r'Test\s+Reports?',
            r'Reports?\s+of\s+the\s+required\s+tests?',
            r'Required\s+tests?'
        ],

        "standards_list": [
            r'List\s+of\s+standards',
            r'Standards?\s+applied\s+to\s+the\s+product'
        ],

        "country_of_origin": [
            r'Country\s+of\s+origin'
        ],

        "product_booklet": [
            r'Product\s+explanatory\s+booklet',
            r'User\s+Manual',
            r'Product\s+Manual'
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

    r'ISOIIEC\s*\d+(?:[-:]\d+)*',

    r'ISO\/IEC\s*\d+(?:[-:]\d+)*',

    r'ISO\s*\d+(?:[-:]\d+)*',

    r'IEC\s*\d+(?:[-:]\d+)*',

    r'SASO[- ]?[A-Z0-9\-]+',

    r'GSO[- ]?[A-Z0-9\-]+',

    r'ASTM[- ]?[A-Z0-9\-]+',

    r'EN\s*\d+(?:[-:]\d+)*',

    r'NFPA\s*\d+(?:[-:]\d+)*',

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



# def normalize_requirements(requirements):

#     normalized = []

#     seen = set()

#     GENERIC_NAMES = {
#         "certificate",
#         "certificates",
#         "report",
#         "reports",
#         "manual",
#         "manuals",
#         "document",
#         "documents"
#     }

#     for req in requirements:

#         name = req.get(
#             "requirement_name",
#             ""
#         ).strip()

#         req_type = req.get(
#             "requirement_type",
#             ""
#         )

#         # -------------------------
#         # Fix OCR issues
#         # -------------------------

#         name = re.sub(
#             r'ISOIIEC',
#             'ISO/IEC',
#             name,
#             flags=re.I
#         )

#         name = re.sub(
#             r'\s+',
#             ' ',
#             name
#         ).strip()

#         # -------------------------
#         # Remove generic names
#         # -------------------------

#         if name.lower() in GENERIC_NAMES:
#             continue

#         # -------------------------
#         # Normalize plurals
#         # -------------------------

#         if name.lower() == "certificates of conformity":
#             name = "Certificate of Conformity"

#         if name.lower() == "declarations of conformity":
#             name = "Declaration of Conformity"

#         if name.lower() == "technical files":
#             name = "Technical File"

#         # -------------------------
#         # Quality Mark is optional
#         # -------------------------

#         if (
#             req_type == "quality_mark"
#             and "saudi quality mark" in name.lower()
#         ):
#             req["mandatory"] = False

#         # -------------------------
#         # Update cleaned name
#         # -------------------------

#         req["requirement_name"] = name

#         # -------------------------
#         # Deduplicate
#         # -------------------------

#         key = (
#             req.get("requirement_type"),
#             name.lower()
#         )

#         if key in seen:
#             continue

#         seen.add(key)

#         normalized.append(req)

#     return normalized




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


NORMALIZATION_MAP = {

    "certificates of conformity":
        "Certificate of Conformity",

    "certificate of conformity":
        "Certificate of Conformity",

    "declarations of conformity":
        "Declaration of Conformity",

    "declaration of conformity":
        "Declaration of Conformity",

    "technical file":
        "Technical File",

    "technical files":
        "Technical File",

    "risk assessment":
        "Risk Assessment Document",

    "risk assessment document":
        "Risk Assessment Document",

    "country of origin":
        "Country of Origin",

    "reports of the required tests":
        "Test Report",

    "required tests":
        "Test Report",

    "test reports":
        "Test Report",

    "test report":
        "Test Report",

    "list of standards":
        "Applied Standards List",

    "standards applied to the product":
        "Applied Standards List",

    "product explanatory booklet":
        "Product Explanatory Booklet",

    "user manual":
        "User Manual",

    "product manual":
        "Product Manual",

    "saudi quality mark":
        "Saudi Quality Mark"
}


def normalize_requirements(requirements):

    normalized = []

    seen = set()

    for req in requirements:

        name = req.get(
            "requirement_name",
            ""
        ).strip()

        req_type = req.get(
            "requirement_type",
            ""
        )

        # --------------------
        # OCR cleanup
        # --------------------

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

        # --------------------
        # Remove generic names
        # --------------------

        if name.lower() in GENERIC_NAMES:
            continue

        # --------------------
        # Normalize names
        # --------------------

        normalized_name = NORMALIZATION_MAP.get(
            name.lower(),
            name
        )

        req["requirement_name"] = normalized_name

        # --------------------
        # Quality mark optional
        # --------------------

        if (
            req_type == "quality_mark"
            and normalized_name.lower() == "saudi quality mark"
        ):
            req["mandatory"] = False

        # --------------------
        # Deduplicate
        # --------------------

        key = (
            req_type,
            normalized_name.lower()
        )

        if key in seen:
            continue

        seen.add(key)

        normalized.append(req)

    return normalized