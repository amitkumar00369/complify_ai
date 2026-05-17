from app.utils.intent_lookup import detect_intents


import re
INTENT_KEYWORDS = {

    # =====================================================
    # PRODUCT SEARCH
    # =====================================================

    "product_search": [

        "find product",
        "search product",
        "search item",
        "find item",
        "show products",
        "find products",
        "find variants",
        "product details",
        "show item",
        "search by model",
        "search by sku",
        "find brand",
        "product info"
    ],

    # =====================================================
    # HS CODE LOOKUP
    # =====================================================

    "hs_code_lookup": [

        "hs code",
        "tariff code",
        "custom code",
        "harmonized code",
        "show hs code",
        "find hs code",
        "products belong to hs code",
        "regulations for hs code"
    ],

    # =====================================================
    # TECHNICAL REGULATION
    # =====================================================

    "technical_regulation_lookup": [

        "technical regulation",
        "technical regulations",
        "tr applies",
        "regulation applies",
        "which regulation",
        "applicable regulation",
        "which tr",
        "find tr",
        "mandatory regulation",
        "regulations apply",
        "show regulations"
    ],

    # =====================================================
    # STANDARD LOOKUP
    # =====================================================

    "standard_lookup": [

        "standard",
        "standards",
        "iec",
        "iso",
        "saso standard",
        "which standard",
        "applicable standard",
        "mandatory clauses",
        "test methods",
        "show clauses",
        "safety clauses",
        "testing clauses"
    ],

    # =====================================================
    # SABER REQUIREMENT
    # =====================================================

    "saber_requirement": [

        "saber",
        "saleem",
        "pcoc",
        "scoc",
        "shipment certificate",
        "regulated product",
        "saber certification",
        "saleem category",
        "can shipment certificate",
        "require saber",
        "require pcoc",
        "require scoc"
    ],

    # =====================================================
    # CERTIFICATE LOOKUP
    # =====================================================

    "certificate_lookup": [

        "certificate",
        "certification",
        "certificate expiry",
        "certificate valid",
        "certificate details",
        "show certificate",
        "expired certificate",
        "missing certificate",
        "certificate number",
        "issued certificate",
        "valid certificate"
    ],

    # =====================================================
    # DOCUMENT REQUIREMENT
    # =====================================================

    "document_requirement": [

        "required documents",
        "documents needed",
        "compliance documents",
        "required files",
        "mandatory documents",
        "show requirements",
        "testing requirements",
        "labeling requirements",
        "packaging requirements",
        "documents required"
    ],

    # =====================================================
    # TECHNICAL SPECIFICATION
    # =====================================================

    "technical_specification": [

        "technical specifications",
        "product specifications",
        "voltage compliance",
        "frequency compliance",
        "material compliance",
        "compare specs",
        "specification validation",
        "power rating",
        "electrical rating"
    ],

    # =====================================================
    # RISK ASSESSMENT
    # =====================================================

    "risk_assessment": [

        "risk",
        "hazard",
        "warning",
        "compliance risks",
        "high-risk",
        "product hazards",
        "missing warning",
        "safety warning",
        "additional testing",
        "risk level"
    ],

    # =====================================================
    # SDOC
    # =====================================================

    "sdoc_validation": [

        "sdoc",
        "validate sdoc",
        "sdoc expiry",
        "sdoc valid",
        "show sdoc",
        "compare sdoc"
    ],

    # =====================================================
    # TECHNICAL REPORT
    # =====================================================

    "technical_report": [

        "technical report",
        "test report",
        "failed test",
        "test results",
        "report validation",
        "lab report",
        "test cases",
        "report pass",
        "report fail"
    ],

    # =====================================================
    # LABEL VALIDATION
    # =====================================================

    "label_validation": [

        "arabic label",
        "warning label",
        "label",
        "country of origin",
        "energy label",
        "logo compliant",
        "arabic present",
        "label validation"
    ],

    # =====================================================
    # COMMERCIAL DOCUMENT
    # =====================================================

    "commercial_document": [

        "invoice",
        "packing list",
        "importer details",
        "shipment quantity",
        "commercial invoice",
        "invoice validation",
        "invoice quantity",
        "shipment documents"
    ],

    # =====================================================
    # CLAUSE LOOKUP
    # =====================================================

    "clause_lookup": [

        "mandatory clauses",
        "show clauses",
        "safety clauses",
        "testing clauses",
        "labeling clauses",
        "explain clause",
        "clause meaning",
        "which clause"
    ],

    # =====================================================
    # COMPLIANCE VALIDATION
    # =====================================================

    "compliance_validation": [

        "fully compliant",
        "missing documents",
        "compliance status",
        "validate compliance",
        "compliance validation",
        "compliance violations",
        "inconsistencies",
        "missing requirements",
        "overall compliance"
    ],

    # =====================================================
    # SMART RECOMMENDATION
    # =====================================================

    "recommendation": [

        "next step",
        "what should i upload",
        "pending",
        "what next",
        "next compliance step",
        "certification pending",
        "required next",
        "upload next"
    ],

    # =====================================================
    # DASHBOARD ANALYTICS
    # =====================================================

    "dashboard_analytics": [

        "expired certificates",
        "non-compliant products",
        "high-risk products",
        "completion percentage",
        "analytics",
        "dashboard",
        "compliance summary",
        "expiring certificates"
    ],

    # =====================================================
    # AI ASSISTANT
    # =====================================================

    "ai_assistant": [

        "what do i need",
        "can i import",
        "can i export",
        "can this product pass",
        "why rejected",
        "explain compliance",
        "help me comply",
        "what standards apply",
        "how to comply"
    ]
}

PRODUCT_ALIASES = {

    # =====================================================
    # CHEMICAL PRODUCTS
    # =====================================================

    "anti dust spray": [
        "anti dust spray",
        "anti-dust spray",
        "dust remover",
        "floor spray",
        "mop spray",
        "spolvero mop"
    ],

    "acrylic top coat": [
        "acrylic top coat",
        "top coat",
        "paint coating",
        "renner coating"
    ],

    "adhesion promoter": [
        "adhesion promoter",
        "adhesion promoter for glass",
        "glass promoter"
    ],

    "detergent": [
        "detergent",
        "cleaning detergent",
        "chemical cleaner"
    ],

    "paint": [
        "paint",
        "varnish",
        "pigment coating"
    ],

    "coating": [
        "coating",
        "surface coating",
        "protective coating"
    ],

    "industrial cleaner": [
        "industrial cleaner",
        "professional cleaner"
    ],

    "spray product": [
        "spray product",
        "chemical spray"
    ],

    # =====================================================
    # ELECTRICAL / KITCHEN PRODUCTS
    # =====================================================

    "cooking range": [
        "cooking range",
        "electric cooking range",
        "plate cooking range",
        "commercial cooker",
        "kitchen cooker"
    ],

    "electric fryer": [
        "electric fryer",
        "deep fat fryer",
        "commercial fryer",
        "berto fryer"
    ],

    "electric kettle": [
        "electric kettle",
        "kettle"
    ],

    "oven": [
        "oven",
        "electric oven",
        "commercial oven"
    ],

    "kitchen appliance": [
        "kitchen appliance",
        "kitchen equipment",
        "food appliance"
    ],

    "commercial appliance": [
        "commercial appliance",
        "commercial equipment"
    ],

    "electrical appliance": [
        "electrical appliance",
        "electrical equipment"
    ],

    # =====================================================
    # FOOD / MACHINERY PRODUCTS
    # =====================================================

    "potato peeler": [
        "potato peeler",
        "professional potato peeler",
        "sap peeler"
    ],

    "food equipment": [
        "food equipment",
        "food machinery",
        "food processing equipment"
    ],

    "machinery": [
        "machinery",
        "machine",
        "industrial machine"
    ],

    # =====================================================
    # COOLING / DISPENSER PRODUCTS
    # =====================================================

    "beverage cooling machine": [
        "beverage cooling machine",
        "beverage cooling machines",
        "beverage cooler",
        "cooling dispenser",
        "drink dispenser",
        "drink cooler"
    ],

    # =====================================================
    # GENERIC
    # =====================================================

    "cleaner": [
        "cleaner",
        "floor cleaner",
        "surface cleaner"
    ],

    "glass product": [
        "glass product",
        "glass material"
    ]
}
CERTIFICATE_TYPES = [
    "PCOC",
    "SCOC",
    "COC",
    "SABER",
    "SDOC"
]


MARKETS = {

    "KSA": [
        "ksa",
        "saudi",
        "saudi arabia",
        "saso",
        "saber"
    ]
}


def extract_query_entities(text: str):

    text_lower = text.lower()

    result = {
        "product_name": None,
        "market": "KSA"
    }

    # =====================================================
    # CREATE ALL ALIAS PAIRS
    # =====================================================

    alias_mapping = []

    for product, aliases in PRODUCT_ALIASES.items():

        for alias in aliases:

            alias_mapping.append(
                (alias, product)
            )

    # =====================================================
    # SORT LONGEST FIRST
    # =====================================================

    alias_mapping.sort(
        key=lambda x: len(x[0]),
        reverse=True
    )

    # =====================================================
    # PRODUCT MATCHING
    # =====================================================

    for alias, product in alias_mapping:

        if alias in text_lower:

            result["product_name"] = product

            print(
                f"Matched product '{product}' "
                f"using alias '{alias}'"
            )

            break

    # =====================================================
    # MARKET DETECTION
    # =====================================================

    market_aliases = {
        "KSA": [
            "ksa",
            "saudi",
            "saudi arabia",
            "saber",
            "saso"
        ]
    }

    for market, aliases in market_aliases.items():

        for alias in aliases:

            if alias in text_lower:

                result["market"] = market
                break

    return result

def extract_query_entities_extended(text: str):

    query = text.lower()

    result = {

        "intent": None,

        "product_name": None,

        "hs_code": None,

        "certificate_type": None,

        "market": "KSA",

        "query_type": "general"
    }

    # ============================================
    # HS CODE
    # ============================================

    hs_match = re.search(r"\b\d{6,12}\b", query)

    if hs_match:

        result["hs_code"] = hs_match.group()

    # ============================================
    # INTENT
    # ============================================

    result["intent"] = detect_intents(text)

    # ============================================
    # PRODUCT
    # ============================================

    alias_mapping = []

    for product, aliases in PRODUCT_ALIASES.items():

        for alias in aliases:

            alias_mapping.append((alias, product))

    alias_mapping.sort(
        key=lambda x: len(x[0]),
        reverse=True
    )

    for alias, product in alias_mapping:

        if alias in query:

            result["product_name"] = product
            break

    # ============================================
    # CERTIFICATE TYPE
    # ============================================

    for cert in CERTIFICATE_TYPES:

        if cert.lower() in query:

            result["certificate_type"] = cert
            break

    # ============================================
    # MARKET
    # ============================================

    for market, aliases in MARKETS.items():

        for alias in aliases:

            if alias in query:

                result["market"] = market
                break

    # ============================================
    # QUERY TYPE
    # ============================================

    if result["hs_code"]:

        result["query_type"] = "hs_code"

    elif result["product_name"]:

        result["query_type"] = "product"

    return result