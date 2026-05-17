import re
from rapidfuzz import fuzz


INTENT_PRIORITY = {

    "hs_code_lookup": 100,

    "standard_lookup": 90,

    "technical_regulation_lookup": 85,

    "saber_requirement": 80,

    "certificate_lookup": 75,

    "document_requirement": 70,

    "market_access": 65,

    "export_eligibility": 60,

    "product_search": 50,

    "ai_assistant": 10
}


INTENT_KEYWORDS = {

    # =====================================================
    # MARKET ACCESS
    # =====================================================

    "market_access": [

        "sell in",
        "market access",
        "allowed in",
        "can be sold",
        "distribute in",
        "sell product",
        "launch in saudi",
        "sell electric",
        "sell cooking range"
    ],

    # =====================================================
    # EXPORT / IMPORT
    # =====================================================

    "export_eligibility": [

        "can i export",
        "export to saudi",
        "allowed to export",
        "can export",

        "can i import",
        "import into saudi",
        "allowed to import"
    ],

    # =====================================================
    # HS CODE
    # =====================================================

    "hs_code_lookup": [

        "hs code",
        "tariff code",
        "custom code",
        "harmonized code",
        "show hs code",
        "find hs code",
        "regulations for hs code"
    ],

    # =====================================================
    # TECHNICAL REGULATION
    # =====================================================

    "technical_regulation_lookup": [

        "technical regulation",
        "technical regulations",
        "which regulation",
        "applicable regulation",
        "find tr",
        "show regulations"
    ],

    # =====================================================
    # STANDARDS
    # =====================================================

    "standard_lookup": [

        "standard",
        "standards",
        "iec",
        "iso",
        "saso standard",
        "which standard",
        "applicable standard"
    ],

    # =====================================================
    # SABER
    # =====================================================

    "saber_requirement": [

        "saber",
        "saleem",
        "pcoc",
        "scoc",
        "shipment certificate",
        "require saber",
        "require pcoc",
        "require scoc"
    ],

    # =====================================================
    # CERTIFICATE
    # =====================================================

    "certificate_lookup": [

        "certificate",
        "certification",
        "certificate expiry",
        "certificate valid",
        "show certificate"
    ],

    # =====================================================
    # DOCUMENTS
    # =====================================================

    "document_requirement": [

        "required documents",
        "documents needed",
        "compliance documents",
        "mandatory documents",
        "documents required"
    ],

    # =====================================================
    # PRODUCT SEARCH
    # =====================================================

    "product_search": [

        "find product",
        "search product",
        "show products",
        "product details",
        "show item"
    ],

    # =====================================================
    # GENERAL AI
    # =====================================================

    "ai_assistant": [

        "what do i need",
        "help me comply",
        "how to comply",
        "why rejected"
    ]
}


def detect_intents(query: str):

    query_lower = query.lower()

    result = {

        "query": query,

        "intents": [],

        "primary_intent": None,

        "intent_scores": {}
    }

    # =====================================================
    # KEYWORD MATCHING
    # =====================================================

    for intent, keywords in INTENT_KEYWORDS.items():

        best_score = 0

        for keyword in keywords:

            # exact match
            if keyword in query_lower:

                score = 100

            else:

                # fuzzy match
                score = fuzz.partial_ratio(
                    keyword,
                    query_lower
                )

            if score > best_score:

                best_score = score

        # threshold
        if best_score >= 75:

            result["intents"].append(intent)

            result["intent_scores"][intent] = best_score

    # =====================================================
    # PRIMARY INTENT
    # =====================================================

    if result["intents"]:

        result["primary_intent"] = max(
            result["intents"],
            key=lambda x: (
                INTENT_PRIORITY.get(x, 0),
                result["intent_scores"][x]
            )
        )

    else:

        result["primary_intent"] = "ai_assistant"

    return result