# # =========================================================
# # FILE: app/utils/query_parser.py
# # =========================================================

# import re


# PRODUCT_ALIASES = {

#     "anti dust spray": [
#         "anti dust spray",
#         "anti-dust spray",
#         "dust remover",
#         "floor spray",
#         "mop spray",
#         "spolvero mop"
#     ],

#     "potato peeler": [
#         "potato peeler",
#         "professional potato peeler",
#         "sap peeler"
#     ],

#     "electric fryer": [
#         "electric fryer",
#         "deep fat fryer",
#         "commercial fryer",
#         "berto fryer"
#     ],

#     "acrylic top coat": [
#         "acrylic top coat",
#         "top coat",
#         "paint coating",
#         "renner coating"
#     ],

#     "adhesion promoter": [
#         "adhesion promoter",
#         "adhesion promoter for glass",
#         "glass promoter"
#     ],

#     "cooking range": [
#         "cooking range",
#         "electric cooking range",
#         "plate cooking range",
#         "commercial cooker",
#         "kitchen cooker"
#     ],

#     "electric kettle": [
#         "electric kettle",
#         "kettle"
#     ],

#     "oven": [
#         "oven",
#         "electric oven",
#         "commercial oven"
#     ],

#     "cleaner": [
#         "cleaner",
#         "floor cleaner",
#         "surface cleaner"
#     ],

#     "paint": [
#         "paint",
#         "varnish",
#         "pigment coating"
#     ],

#     "detergent": [
#         "detergent",
#         "cleaning detergent",
#         "chemical cleaner"
#     ],

#     "kitchen appliance": [
#         "kitchen appliance",
#         "kitchen equipment",
#         "food appliance"
#     ],

#     "machinery": [
#         "machinery",
#         "machine",
#         "industrial machine"
#     ],

#     "coating": [
#         "coating",
#         "surface coating",
#         "protective coating"
#     ],

#     "glass product": [
#         "glass product",
#         "glass material"
#     ],

#     "food equipment": [
#         "food equipment",
#         "food machinery",
#         "food processing equipment"
#     ],

#     "industrial cleaner": [
#         "industrial cleaner",
#         "professional cleaner"
#     ],

#     "spray product": [
#         "spray product",
#         "chemical spray"
#     ],

#     "commercial appliance": [
#         "commercial appliance",
#         "commercial equipment"
#     ],

#     "electrical appliance": [
#         "electrical appliance",
#         "electrical equipment"
#     ]
# }


# def extract_query_entities(text: str):

#     text_lower = text.lower()

#     result = {
#         "product_name": None,
#         "market": "KSA"
#     }

#     # --------------------------------------
#     # CREATE ALL ALIAS PAIRS
#     # --------------------------------------

#     alias_mapping = []

#     for product, aliases in PRODUCT_ALIASES.items():

#         for alias in aliases:

#             alias_mapping.append(
#                 (alias, product)
#             )

#     # --------------------------------------
#     # SORT LONGEST FIRST
#     # --------------------------------------

#     alias_mapping.sort(
#         key=lambda x: len(x[0]),
#         reverse=True
#     )

#     # --------------------------------------
#     # MATCH
#     # --------------------------------------

#     for alias, product in alias_mapping:

#         if alias in text_lower:

#             result["product_name"] = product

#             print(
#                 f"Matched product '{product}' using alias '{alias}'"
#             )

#             break

#     # --------------------------------------
#     # MARKET
#     # --------------------------------------

#     if "ksa" in text_lower:
#         result["market"] = "KSA"

#     return result

# =========================================================
# FILE: app/utils/query_parser.py
# =========================================================

import re


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