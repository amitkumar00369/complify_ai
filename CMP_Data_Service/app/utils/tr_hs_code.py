# import re
# from typing import List, Dict


# def extract_product_hs_codes(
#     raw_text: str,
#     scope: dict
# ) -> List[Dict]:

#     """
#     Extract:
#     - serial number
#     - product
#     - HS / customs codes

#     Supports:
#     - 4 digit HS codes
#     - 6 digit HS codes
#     - 8 digit HS codes
#     - spaced OCR HS codes
#     """
#     print(raw_text)

#     # -----------------------------
#     # CLEAN TEXT
#     # -----------------------------
#     text = raw_text.replace("\n", " ")

#     # remove page numbers
#     text = re.sub(
#         r"Page\s+\d+\s+of\s+\d+",
#         " ",
#         text,
#         flags=re.I
#     )

#     # remove document ids
#     text = re.sub(
#         r"\b\d{2}-\d{2}-\d{2}-\d{3}\b",
#         " ",
#         text
#     )

#     # remove website/footer
#     text = re.sub(
#         r'WWW\.SASO\.GOV\.SA',
#         ' ',
#         text,
#         flags=re.I
#     )

#     # normalize spaces
#     text = re.sub(r"\s+", " ", text).strip()

#     # -----------------------------
#     # SLICE REQUIRED PART
#     # -----------------------------
#     start = scope.get("start")
#     end = scope.get("end")

#     if start:

#         start_match = re.search(
#             re.escape(start),
#             text,
#             re.I
#         )

#         if start_match:
#             text = text[start_match.end():]

#     if end:

#         stop_match = re.search(
#             re.escape(end),
#             text,
#             re.I
#         )

#         if stop_match:
#             text = text[:stop_match.start()]

#     # -----------------------------
#     # REMOVE COMMON TABLE HEADERS
#     # -----------------------------
#     text = re.sub(
#         r"No\.\s*Product\s*HS\s*Code",
#         " ",
#         text,
#         flags=re.I
#     )

#     text = re.sub(
#         r"Product\s*Categories\s*HS\s*Code",
#         " ",
#         text,
#         flags=re.I
#     )

#     text = re.sub(
#         r"Product\s*categories\s*Customs\s*item",
#         " ",
#         text,
#         flags=re.I
#     )

#     # -----------------------------
#     # FIND REAL ROW STARTS
#     # -----------------------------
#     row_matches = list(
#         re.finditer(
#             r"\b(\d{1,2})\s+(?=[A-Z])",
#             text
#         )
#     )

#     results = []

#     for i, match in enumerate(row_matches):

#         no = int(match.group(1))

#         start_pos = match.start()

#         if i + 1 < len(row_matches):
#             end_pos = row_matches[i + 1].start()
#         else:
#             end_pos = len(text)

#         row = text[start_pos:end_pos].strip()

#         # -----------------------------
#         # REMOVE SERIAL NUMBER
#         # -----------------------------
#         row = re.sub(
#             r"^\d{1,2}\s+",
#             "",
#             row
#         ).strip()

#         # -----------------------------
#         # REMOVE OCR GARBAGE
#         # -----------------------------
#         row = re.sub(
#             r'Annex\s+No\.\s*\(\d+\).*',
#             ' ',
#             row,
#             flags=re.I
#         )

#         row = re.sub(
#             r'\.tf',
#             ' ',
#             row
#         )

#         # remove note leakage
#         row = re.split(
#             r'\bNote\s*:',
#             row,
#             flags=re.I
#         )[0]

#         # remove footer leakage
#         row = re.sub(
#             r'WWW\.SASO\.GOV\.SA',
#             ' ',
#             row,
#             flags=re.I
#         )

#         # normalize spaces
#         row = re.sub(r"\s+", " ", row).strip()

#         # -----------------------------
#         # EXTRACT HS CODES
#         # -----------------------------
#         raw_codes = re.findall(
#             r"""
#             \b
#             (
#                 \d{4}
#                 (?:\s?\d{2})?
#                 (?:\s?\d{2})?
#             )
#             \b
#             """,
#             row,
#             flags=re.VERBOSE
#         )

#         hs_codes = []

#         for code in raw_codes:

#             # remove spaces
#             code = re.sub(r"\s+", "", code)

#             # valid lengths
#             if len(code) not in [4, 6, 8]:
#                 continue

#             # skip years
#             if code.startswith(("19", "20")):
#                 continue

#             if code not in hs_codes:
#                 hs_codes.append(code)

#         if not hs_codes:
#             continue

#         # -----------------------------
#         # REMOVE HS CODES FROM PRODUCT
#         # -----------------------------
#         product = re.sub(
#             r"""
#             \b
#             \d{4}
#             (?:\s?\d{2})?
#             (?:\s?\d{2})?
#             \b
#             """,
#             " ",
#             row,
#             flags=re.VERBOSE
#         )

#         # cleanup spaces
#         product = re.sub(r"\s+", " ", product)

#         product = product.strip(" .,-")

#         # -----------------------------
#         # APPEND
#         # -----------------------------
#         results.append({
#             "no": no,
#             "product": product,
#             "hs_code": hs_codes
#         })

#     return results

import re
from typing import List, Dict


# =========================================================
# COMMON CLEANER
# =========================================================
def clean_ocr_text(text: str) -> str:

    text = text.replace("\n", " ")

    # remove page text
    text = re.sub(
        r'Page\s+\d+\s+(?:of|from)\s+\d+',
        ' ',
        text,
        flags=re.I
    )

    # remove document ids
    text = re.sub(
        r'\b\d{2}-\d{2}-\d{2}-\d{3}\b',
        ' ',
        text
    )

    # remove website/footer
    text = re.sub(
        r'WWW\.SASO\.GOV\.SA',
        ' ',
        text,
        flags=re.I
    )

    # remove organization names
    text = re.sub(
        r'Saudi Standards Organization',
        ' ',
        text,
        flags=re.I
    )

    # normalize spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# =========================================================
# GENERIC HS CODE EXTRACTOR
# =========================================================
def extract_hs_codes(text: str) -> List[str]:

    raw_codes = re.findall(
        r"""
        \b
        (
            \d{4}
            (?:\s?\d{2})?
            (?:\s?\d{2})?
        )
        \b
        """,
        text,
        flags=re.VERBOSE
    )

    hs_codes = []

    for code in raw_codes:

        code = re.sub(r'\s+', '', code)

        # valid hs lengths
        if len(code) not in [4, 6, 8]:
            continue

        # skip years
        if code.startswith(("19", "20")):
            continue

        if code not in hs_codes:
            hs_codes.append(code)

    return hs_codes


# =========================================================
# TYPE 1 -> SIMPLE SERIAL TABLE
# =========================================================
def parse_simple_table(text: str) -> List[Dict]:

    # remove headers
    text = re.sub(
        r'No\.\s*Product.*?HS\s*Code',
        ' ',
        text,
        flags=re.I
    )

    text = re.sub(
        r'Product\s*categories\s*Customs\s*item',
        ' ',
        text,
        flags=re.I
    )

    row_matches = list(
        re.finditer(
            r'\b(\d{1,2})\s+(?=[A-Z])',
            text
        )
    )

    results = []

    for i, match in enumerate(row_matches):

        no = int(match.group(1))

        start = match.start()

        if i + 1 < len(row_matches):
            end = row_matches[i + 1].start()
        else:
            end = len(text)

        row = text[start:end].strip()

        # remove serial
        row = re.sub(
            r'^\d{1,2}\s+',
            '',
            row
        ).strip()

        # remove note leakage
        row = re.split(
            r'\bNote\s*:',
            row,
            flags=re.I
        )[0]

        # extract hs codes
        hs_codes = extract_hs_codes(row)

        if not hs_codes:
            continue

        # remove hs codes from product
        product = re.sub(
            r"""
            \b
            \d{4}
            (?:\s?\d{2})?
            (?:\s?\d{2})?
            \b
            """,
            ' ',
            row,
            flags=re.VERBOSE
        )

        product = re.sub(r'\s+', ' ', product)

        product = product.strip(' .,-')

        results.append({
            "no": no,
            "product": product,
            "hs_code": hs_codes
        })

    return results


# =========================================================
# TYPE 2 -> GROUPED TABLE
# =========================================================
def parse_grouped_table(text: str) -> List[Dict]:

    print("text", text)

    # ---------------------------------------------------
    # REMOVE HEADERS
    # ---------------------------------------------------
    text = re.sub(
        r'B\)\s*List\s*of\s*Products\s*and\s*HS\s*Codes',
        ' ',
        text,
        flags=re.I
    )

    text = re.sub(
        r'List\s*of\s*Products\s*and\s*HS\s*Codes',
        ' ',
        text,
        flags=re.I
    )

    text = re.sub(
        r'Product\s*Category\s*Item\s*HS\s*Code',
        ' ',
        text,
        flags=re.I
    )

    # ---------------------------------------------------
    # REMOVE NOTE SECTION
    # ---------------------------------------------------
    text = re.split(
        r'\bNote\s*:',
        text,
        flags=re.I
    )[0]

    # normalize spaces
    text = re.sub(r'\s+', ' ', text).strip()

    # ---------------------------------------------------
    # FIND REAL HS CODE POSITIONS
    # ---------------------------------------------------
    hs_matches = list(
        re.finditer(
            r'''
            (?<!item\s)
            (?<!chapter\s)
            (?<!heading\s)
            (?<!\d,\s)

            (
                \d{4}
                (?:\d{2})?
                (?:\d{2})?
            )

            (?=
                \s+[A-Z]
                |
                \s*$
                |
                \s*-
            )

            (?!\s*,)
            (?!\s+and\s+\d)
            ''',
            text,
            flags=re.VERBOSE | re.I
        )
    )

    results = []

    previous_end = 0

    current_category = None

    # ---------------------------------------------------
    # GENERIC CATEGORY PATTERN
    # ---------------------------------------------------
    CATEGORY_PATTERN = r'''
        [A-Z][A-Za-z\s\(\)\-\/&,]{5,80}
    '''

    for match in hs_matches:

        hs_code = match.group(1)

        block = text[previous_end:match.start()].strip()

        previous_end = match.end()

        if not block:
            continue

        # ---------------------------------------------------
        # DETECT CATEGORY
        # ---------------------------------------------------
        # ---------------------------------------------------
# DETECT CATEGORY DYNAMICALLY
# ---------------------------------------------------

        candidate_lines = re.findall(
            r'''
            [A-Z]
            [A-Za-z\s\(\)\-\/&,]{5,60}
            ''',
            block,
            flags=re.VERBOSE
        )

        for candidate in reversed(candidate_lines):

            candidate = candidate.strip(" .,-")

            words = candidate.split()

            # probable category heuristics
            if (
                2 <= len(words) <= 8
                and candidate[0].isupper()
                and len(candidate) < 60
            ):

                # avoid long sentence fragments
                if not re.search(
                    r'\b(containing|calculated|dispersed|dissolved)\b',
                    candidate,
                    re.I
                ):

                    current_category = candidate
                    break

        item = block

        # ---------------------------------------------------
        # REMOVE CATEGORY FROM ITEM
        # ---------------------------------------------------
        if current_category:

            item = re.sub(
                re.escape(current_category),
                '',
                item,
                flags=re.I
            )

        # ---------------------------------------------------
        # REMOVE INLINE HS REFERENCES
        # ---------------------------------------------------
        item = re.sub(
            r'item\s+\d{4}(?:,\s*\d{4})*(?:\s+and\s+\d{4})?',
            ' ',
            item,
            flags=re.I
        )

        # remove trailing connectors
        item = re.sub(
            r'\b(and|or)\s*$',
            ' ',
            item,
            flags=re.I
        )

        # ---------------------------------------------------
        # GENERIC OCR ROW SPLIT
        # ---------------------------------------------------
        candidate_matches = list(
            re.finditer(
                r'''
                (?:
                    \.\s+
                    |
                    --\s+
                    |
                    \)\s+
                )

                (
                    [A-Z][A-Za-z\s\-/&,]{8,80}
                )
                ''',
                item,
                flags=re.VERBOSE
            )
        )

        for candidate in candidate_matches:

            split_index = candidate.start(1)

            # avoid cutting short valid rows
            if split_index < 120:
                continue

            left = item[:split_index].strip()
            right = item[split_index:].strip()

            # probable new logical row
            if (
                len(right.split()) >= 3
                and len(left.split()) >= 5
            ):

                item = left
                break

        # ---------------------------------------------------
        # CUT WHEN CATEGORY REPEATS
        # ---------------------------------------------------
        if current_category:

            repeated = list(
                re.finditer(
                    re.escape(current_category),
                    item,
                    flags=re.I
                )
            )

            if len(repeated) >= 2:

                item = item[:repeated[1].start()].strip()

        # ---------------------------------------------------
        # CLEANUP
        # ---------------------------------------------------
        item = re.sub(r'\s+', ' ', item)

        item = item.strip(' .,-')

        # ---------------------------------------------------
        # REJECT WEAK FRAGMENTS
        # ---------------------------------------------------
        if len(item.split()) < 4:
            continue

        if not item:
            continue

        results.append({
            "product_category": current_category,
            "item": item,
            "hs_code": [hs_code]
        })

    return results


# =========================================================
# MAIN GENERIC ROUTER
# =========================================================
def extract_product_hs_codes(
    raw_text: str,
    scope: dict = None
) -> List[Dict]:

    text = clean_ocr_text(raw_text)

    # -----------------------------------------
    # SCOPE CUTTING
    # -----------------------------------------
    if scope:

        start = scope.get("start")
        end = scope.get("end")

        if start:

            start_match = re.search(
                re.escape(start),
                text,
                re.I
            )

            if start_match:
                text = text[start_match.end():]

        if end:

            end_match = re.search(
                re.escape(end),
                text,
                re.I
            )

            if end_match:
                text = text[:end_match.start()]

    # -----------------------------------------
    # DETECT TABLE TYPE
    # -----------------------------------------
    serial_rows = re.findall(
        r'\b\d{1,2}\s+[A-Z]',
        text
    )

    hs_codes = extract_hs_codes(text)

    # -----------------------------------------
    # TYPE 1 -> SERIAL TABLE
    # -----------------------------------------
    if len(serial_rows) >= 5:

        return parse_simple_table(text)

    # -----------------------------------------
    # TYPE 2 -> GROUPED TABLE
    # -----------------------------------------
    if len(hs_codes) >= 5:

        return parse_grouped_table(text)

    return []