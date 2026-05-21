import re
from typing import List, Dict


def extract_product_hs_codes(
    raw_text: str,
    scope: dict
) -> List[Dict]:

    """
    Extract product + hs codes between start_text and stop_text
    """

    # -----------------------------
    # CLEAN TEXT
    # -----------------------------
    text = raw_text.replace("\n", " ")

    # remove page numbers
    text = re.sub(
        r"Page\s+\d+\s+of\s+\d+",
        " ",
        text,
        flags=re.I
    )

    # remove repeated document ids
    text = re.sub(
        r"\b\d{2}-\d{2}-\d{2}-\d{3}\b",
        " ",
        text
    )

    # normalize spaces
    text = re.sub(r"\s+", " ", text).strip()

    # -----------------------------
    # SLICE REQUIRED PART
    # -----------------------------
    start_match = re.search(
        re.escape(scope.get("start")),
        text,
        re.I
    )

    if not start_match:
        return []

    start_index = start_match.end()

    stop_match = re.search(
        re.escape(scope.get("end")),
        text[start_index:],
        re.I
    )

    if stop_match:
        end_index = start_index + stop_match.start()
        text = text[start_index:end_index]
    else:
        text = text[start_index:]

    # -----------------------------
    # REMOVE TABLE HEADER
    # -----------------------------
    text = re.sub(
        r"No\.\s*Product\s*HS\s*Code",
        " ",
        text,
        flags=re.I
    )

    # -----------------------------
    # FIND ROWS
    # -----------------------------
    rows = re.findall(
        r'(\d{1,2}\s+.*?)(?=\s+\d{1,2}\s+[A-Za-z]|$)',
        text
    )

    results = []

    for row in rows:

        row = row.strip()

        if not row:
            continue

        # -----------------------------
        # SERIAL NUMBER
        # -----------------------------
        no_match = re.match(
            r"^(\d{1,2})\s+",
            row
        )

        if not no_match:
            continue

        no = int(no_match.group(1))

        row = row[no_match.end():].strip()

        # -----------------------------
        # REMOVE OCR GARBAGE
        # -----------------------------
        row = re.sub(
            r'Annex\s+No\.\s*\(\d+\).*',
            ' ',
            row,
            flags=re.I
        )

        row = re.sub(
            r'\s+\b\d\b\s+',
            ' ',
            row
        )

        # remove random OCR tokens
        row = re.sub(
            r'\.tf',
            ' ',
            row
        )

        # -----------------------------
        # EXTRACT HS CODES
        # -----------------------------

        # normal hs codes
        normal_codes = re.findall(
            r"\b\d{8}\b",
            row
        )

        # spaced hs codes
        spaced_codes = re.findall(
            r"(?<!\d)(\d{4}\s\d{4})(?!\d)",
            row
        )

        valid_codes = []

        # validate normal codes
        for code in normal_codes:

            if code.startswith(("39", "63")):
                valid_codes.append(code)

        # validate spaced codes
        for code in spaced_codes:

            code = code.replace(" ", "")

            if code.startswith(("39", "63")):
                valid_codes.append(code)

        # unique hs codes
        hs_codes = list(dict.fromkeys(valid_codes))

        if not hs_codes:
            continue

        # -----------------------------
        # REMOVE HS CODES FROM PRODUCT
        # -----------------------------
        product = row

        # remove normal codes
        product = re.sub(
            r"\b\d{8}\b",
            " ",
            product
        )

        # remove spaced codes
        product = re.sub(
            r"\b\d{4}\s\d{4}\b",
            " ",
            product
        )

        # cleanup spaces
        product = re.sub(r"\s+", " ", product)

        product = product.strip(" .,-")

        # -----------------------------
        # APPEND
        # -----------------------------
        if product:
            results.append({
                "no": no,
                "product": product,
                "hs_code": hs_codes
            })

    return results