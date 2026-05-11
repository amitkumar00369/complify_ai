import re
from typing import List, Dict, Any


# =========================================================
# ENTITY EXTRACTOR
# =========================================================

class EntityExtractor:

    # ==========================================
    # MANUFACTURER PATTERNS
    # ==========================================

    MANUFACTURER_PATTERNS = [

        r'manufacturer\s*(?:name)?\s*[:\-]?\s*([a-zA-Z0-9\s\.\-&(),]+)',

        r'manufactured\s+by\s*[:\-]?\s*([a-zA-Z0-9\s\.\-&(),]+)',

        r'producer\s*[:\-]?\s*([a-zA-Z0-9\s\.\-&(),]+)',

        r'company\s*[:\-]?\s*([a-zA-Z0-9\s\.\-&(),]+)'
    ]

    # ==========================================
    # PRODUCT NAME PATTERNS
    # ==========================================

    PRODUCT_NAME_PATTERNS = [

        r'product\s*name\s*[:\-]?\s*([a-zA-Z0-9\s\.\-/&,]+)',

        r'product\s*description\s*[:\-]?\s*([a-zA-Z0-9\s\.\-/&,]+)',

        r'sample\s*description\s*[:\-]?\s*([a-zA-Z0-9\s\.\-/&,]+)'
    ]

    # ==========================================
    # MODEL PATTERNS
    # ==========================================

    MODEL_PATTERNS = [

        r'model\s*type\s*[:\-]?\s*([a-zA-Z0-9\-_]+)',

        r'model\s*name\s*[:\-]?\s*([a-zA-Z0-9\-_]+)',

        r'model\s*number\s*[:\-]?\s*([a-zA-Z0-9\-_]+)',

        r'model\s*[:\-]?\s*([a-zA-Z0-9\-_]+)'
    ]

    # ==========================================
    # COUNTRY PATTERNS
    # ==========================================

    COUNTRY_PATTERNS = [

        r'country\s*of\s*origin\s*[:\-]?\s*([a-zA-Z\s]+)'
    ]

    # ==========================================
    # HS CODE PATTERNS
    # ==========================================

    HS_CODE_PATTERNS = [

        r'hs\s*code\s*[:\-]?\s*(\d{4,12})'
    ]

    # ==========================================
    # GENERIC EXTRACTOR
    # ==========================================

    @staticmethod
    def extract_value(
        text: str,
        patterns: List[str],
        stop_words: List[str] = None,
        max_length: int = 120
    ):

        if not text:
            return None

        stop_words = stop_words or []

        cleaned_text = re.sub(
            r'\s+',
            ' ',
            text
        )

        for pattern in patterns:

            match = re.search(
                pattern,
                cleaned_text,
                re.IGNORECASE
            )

            if match:

                value = (
                    match.group(1)
                    .strip()
                )

                # ==================================
                # HARD LENGTH LIMIT
                # ==================================

                value = value[:max_length]

                # ==================================
                # SPLIT USING STOP WORDS
                # ==================================

                for stop_word in stop_words:

                    value = re.split(
                        stop_word,
                        value,
                        flags=re.IGNORECASE
                    )[0].strip()

                # ==================================
                # REMOVE GARBAGE SYMBOLS
                # ==================================

                value = re.sub(
                    r'[/\\(){}\[\]]',
                    ' ',
                    value
                )

                value = re.sub(
                    r'\s+',
                    ' ',
                    value
                ).strip()

                return value

        return None

    # ==========================================
    # MANUFACTURER
    # ==========================================

    @staticmethod
    def extract_manufacturer(text: str):

        return EntityExtractor.extract_value(

            text=text,

            patterns=(
                EntityExtractor
                .MANUFACTURER_PATTERNS
            ),

            stop_words=[
                "manufacturer address",
                "product name",
                "trademark",
                "country of origin",
                "report number",
                "product test data"
            ]
        )

    # ==========================================
    # PRODUCT NAME
    # ==========================================

    @staticmethod
    def extract_product_name(text: str):

        return EntityExtractor.extract_value(

            text=text,

            patterns=(
                EntityExtractor
                .PRODUCT_NAME_PATTERNS
            ),

            stop_words=[
                "product description",
                "manufacturer",
                "country of origin",
                "trademark",
                "report number",
                "technical regulation"
            ]
        )

    # ==========================================
    # MODEL
    # ==========================================

    @staticmethod
    def extract_model(text: str):

        return EntityExtractor.extract_value(

            text=text,

            patterns=(
                EntityExtractor
                .MODEL_PATTERNS
            ),

            stop_words=[
                "trade mark",
                "trademark",
                "country of origin",
                "product name",
                "page",
                "back"
            ],

            max_length=50
        )

    # ==========================================
    # COUNTRY
    # ==========================================

    @staticmethod
    def extract_country(text: str):

        return EntityExtractor.extract_value(

            text=text,

            patterns=(
                EntityExtractor
                .COUNTRY_PATTERNS
            ),

            stop_words=[
                "hs code",
                "technical regulation",
                "manufacturer"
            ]
        )

    # ==========================================
    # HS CODE
    # ==========================================

    @staticmethod
    def extract_hs_code(text: str):

        return EntityExtractor.extract_value(

            text=text,

            patterns=(
                EntityExtractor
                .HS_CODE_PATTERNS
            ),

            max_length=20
        )


# =========================================================
# REGEX PATTERNS
# =========================================================

TECHNICAL_REGULATION_PATTERN = re.compile(
    r"(technical regulation for [a-zA-Z0-9\s\-\(\)&]+)",
    re.IGNORECASE
)

STANDARD_PATTERN = re.compile(
    r"(iec\s*\d+(?:[-–]\d+)*)|"
    r"(en\s*\d+(?:[-–]\d+)*)|"
    r"(iso\s*\d+(?:[-–]\d+)*)|"
    r"(saso\s*gso\s*\d+(?::\d+)?)",
    re.IGNORECASE
)


# =========================================================
# CONSTANTS
# =========================================================

STOP_WORDS = {
    "manufacturer",
    "product",
    "report",
    "country",
    "address"
}

CERTIFICATION_KEYWORDS = (
    "certificate of conformity",
    "coc",
    "pcoc"
)

TEST_REPORT_KEYWORDS = (
    "test report",
    "report number",
    "cb report"
)

PRODUCT_IDENTIFICATION_KEYWORDS = (
    "product name",
    "model type",
    "product description"
)


# =========================================================
# HELPER
# =========================================================

def build_clause(
    clause_type: str,
    value: Any = None,
    confidence: float = 0.90
) -> Dict[str, Any]:

    clause = {
        "type": clause_type,
        "confidence": confidence
    }

    if value is not None:
        clause["value"] = value

    return clause


# =========================================================
# MAIN EXTRACTION FUNCTION
# =========================================================

def extract_clauses(text: str) -> List[Dict[str, Any]]:

    if not text:
        return []

    text_lower = text.lower()

    clauses: List[Dict[str, Any]] = []

    # =====================================================
    # TECHNICAL REGULATION
    # =====================================================

    for match in TECHNICAL_REGULATION_PATTERN.findall(text_lower):

        regulation = match.strip()

        for stop_word in STOP_WORDS:

            if stop_word in regulation:

                regulation = (
                    regulation
                    .split(stop_word)[0]
                    .strip()
                )

        clauses.append(
            build_clause(
                clause_type="Technical Regulation",
                value=regulation.title(),
                confidence=0.90
            )
        )

    # =====================================================
    # STANDARDS
    # =====================================================

    standard_matches = STANDARD_PATTERN.findall(text_lower)

    for match_group in standard_matches:

        standard = next(
            (item for item in match_group if item),
            None
        )

        if standard:

            clauses.append(
                build_clause(
                    clause_type="Standard",
                    value=standard.upper(),
                    confidence=0.95
                )
            )

    # =====================================================
    # CERTIFICATION
    # =====================================================

    if any(
        keyword in text_lower
        for keyword in CERTIFICATION_KEYWORDS
    ):

        clauses.append(
            build_clause(
                clause_type="Certification",
                value="COC",
                confidence=0.90
            )
        )

    # =====================================================
    # TEST REPORT
    # =====================================================

    if any(
        keyword in text_lower
        for keyword in TEST_REPORT_KEYWORDS
    ):

        clauses.append(
            build_clause(
                clause_type="Test Report",
                value=True,
                confidence=0.85
            )
        )

    # =====================================================
    # PRODUCT IDENTIFICATION
    # =====================================================

    if any(
        keyword in text_lower
        for keyword in PRODUCT_IDENTIFICATION_KEYWORDS
    ):

        clauses.append(
            build_clause(
                clause_type="Product Identification",
                confidence=0.90
            )
        )

    # =====================================================
    # ENTITY EXTRACTION
    # =====================================================

    manufacturer = (
        EntityExtractor.extract_manufacturer(
            text
        )
    )

    if manufacturer:

        clauses.append(
            build_clause(
                clause_type="Manufacturer",
                value=manufacturer,
                confidence=0.95
            )
        )

    product_name = (
        EntityExtractor.extract_product_name(
            text
        )
    )

    if product_name:

        clauses.append(
            build_clause(
                clause_type="Product Name",
                value=product_name,
                confidence=0.93
            )
        )

    model = (
        EntityExtractor.extract_model(
            text
        )
    )

    if model:

        clauses.append(
            build_clause(
                clause_type="Model",
                value=model,
                confidence=0.92
            )
        )

    country = (
        EntityExtractor.extract_country(
            text
        )
    )

    if country:

        clauses.append(
            build_clause(
                clause_type="Country Of Origin",
                value=country,
                confidence=0.88
            )
        )

    hs_code = (
        EntityExtractor.extract_hs_code(
            text
        )
    )

    if hs_code:

        clauses.append(
            build_clause(
                clause_type="HS Code",
                value=hs_code,
                confidence=0.95
            )
        )

    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    unique_clauses = []

    seen = set()

    for clause in clauses:

        key = (
            clause.get("type"),
            clause.get("value")
        )

        if key not in seen:

            seen.add(key)

            unique_clauses.append(clause)

    return unique_clauses