import re
from ..services.llama_service import generate_aliases_llm

def extract_hs_mapping(text: str):

    lines = text.split("\n")

    hs_map = []
    current_hs = None
    products = []

    for line in lines:
        line = line.strip()

        hs_match = re.search(r"\b\d{4}\b", line)

        if hs_match:
            if current_hs and products:
                hs_map.append({
                    "hs_code": current_hs,
                    "products": list(set(products)),
                    "aliases": generate_aliases_llm(products)
                })

            current_hs = hs_match.group()
            products = []
            continue

        if len(line) > 3:
            products.append(line)

    return hs_map