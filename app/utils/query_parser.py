# =========================================================
# FILE: app/utils/query_parser.py
# =========================================================

import re


PRODUCT_ALIASES = {

    "anti dust spray": [
        "anti dust spray",
        "anti-dust spray",
        "dust remover",
        "floor spray",
        "mop spray",
        "spolvero mop"
    ],

    "potato peeler": [
        "potato peeler",
        "professional potato peeler",
        "sap peeler"
    ],

    "electric fryer": [
        "electric fryer",
        "deep fat fryer",
        "commercial fryer",
        "berto fryer"
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

    "cooking range": [
        "cooking range",
        "electric cooking range",
        "plate cooking range",
        "commercial cooker",
        "kitchen cooker"
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

    "cleaner": [
        "cleaner",
        "floor cleaner",
        "surface cleaner"
    ],

    "paint": [
        "paint",
        "varnish",
        "pigment coating"
    ],

    "detergent": [
        "detergent",
        "cleaning detergent",
        "chemical cleaner"
    ],

    "kitchen appliance": [
        "kitchen appliance",
        "kitchen equipment",
        "food appliance"
    ],

    "machinery": [
        "machinery",
        "machine",
        "industrial machine"
    ],

    "coating": [
        "coating",
        "surface coating",
        "protective coating"
    ],

    "glass product": [
        "glass product",
        "glass material"
    ],

    "food equipment": [
        "food equipment",
        "food machinery",
        "food processing equipment"
    ],

    "industrial cleaner": [
        "industrial cleaner",
        "professional cleaner"
    ],

    "spray product": [
        "spray product",
        "chemical spray"
    ],

    "commercial appliance": [
        "commercial appliance",
        "commercial equipment"
    ],

    "electrical appliance": [
        "electrical appliance",
        "electrical equipment"
    ]
}


def extract_query_entities(text: str):

    text_lower = text.lower()

    result = {
        "product_name": None,
        "market": "KSA"
    }

    # --------------------------------------
    # PRODUCT DETECTION
    # --------------------------------------

    for product, aliases in PRODUCT_ALIASES.items():

        for alias in aliases:

            if alias in text_lower:

                result["product_name"] = product
                break

    # --------------------------------------
    # MARKET DETECTION
    # --------------------------------------

    if "ksa" in text_lower:
        result["market"] = "KSA"

    return result