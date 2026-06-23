# import re


# def extract_standards(text):

#     # ----------------------------------
#     # Remove unwanted sections
#     # ----------------------------------

#     stop = re.search(
#         r'B\)\s*List\s+of\s+Products\s+and\s+Customs\s+Coding',
#         text,
#         flags=re.I
#     )

#     if stop:
#         text = text[:stop.start()]

#     text = re.sub(
#         r'Page\s+\d+\s+of\s+\d+',
#         ' ',
#         text,
#         flags=re.I
#     )

#     text = re.sub(
#         r'WWW\.SASO\.GOV\.SA',
#         ' ',
#         text,
#         flags=re.I
#     )

#     text = re.sub(
#         r'\d{2}-\d{2}-\d{2}-\d+',
#         ' ',
#         text
#     )

#     text = re.sub(r'\s+', ' ', text)

#     # ----------------------------------
#     # Standard pattern
#     # ----------------------------------

#     std_pattern = re.compile(
#         r'SASO[- ]?(?:ISO|IEC|ASTM|GSO)[- ]?[A-Z0-9\- ]+?(?=\s+\d+\s+|Note:|$)',
#         re.I
#     )

#     matches = list(std_pattern.finditer(text))

#     results = []

#     for idx, match in enumerate(matches):

#         standard = match.group().strip()

#         standard = re.sub(r'\s+', ' ', standard)

#         # remove OCR garbage
#         standard = re.sub(r'\s+Note$', '', standard, flags=re.I)

#         block_start = (
#             matches[idx - 1].end()
#             if idx > 0
#             else 0
#         )

#         block_end = match.start()

#         block = text[block_start:block_end]

#         # serial number
#         serials = re.findall(r'\b(\d{1,2})\b', block)

#         no = None

#         if serials:
#             no = int(serials[-1])

#         # English title only
#         english_sentences = re.findall(
#             r'[A-Z][A-Za-z0-9 ,:\-\(\)/\.]+',
#             block
#         )

#         title = max(
#             english_sentences,
#             key=len,
#             default=""
#         )

#         title = re.sub(r'\s+', ' ', title).strip()

#         results.append({
#             "no": no,
#             "standard": standard,
#             "title": title
#         })
#         for idx, item in enumerate(results, start=1):

#             item["no"] = idx

#             item["standard"] = re.sub(
#                 r'\s+',
#                 ' ',
#                 item["standard"]
#             ).strip()

#             item["standard"] = re.sub(
#                 r'(\d+-)\s+(\d+)',
#                 r'\1\2',
#                 item["standard"]
#             )

#     return results


# import re


# def extract_standards(text):
#     """
#     Extract:
#     [
#         {
#             "no": 1,
#             "title": "Motorcycles - General Safety Requirements",
#             "standard": "SASO GSO 1798"
#         }
#     ]
#     """

#     # --------------------------------------------------
#     # Keep only Standards section
#     # --------------------------------------------------

#     stop = re.search(
#         r'B\)\s*(?:List\s+of\s+Products|Customs\s+Coding)',
#         text,
#         flags=re.I
#     )

#     if stop:
#         text = text[:stop.start()]

#     # --------------------------------------------------
#     # Cleanup OCR garbage
#     # --------------------------------------------------

#     text = re.sub(
#         r'Page\s+\d+\s+of\s+\d+',
#         ' ',
#         text,
#         flags=re.I
#     )

#     text = re.sub(
#         r'WWW\.SASO\.GOV\.SA',
#         ' ',
#         text,
#         flags=re.I
#     )

#     text = re.sub(
#         r'\d{2}-\d{2}-\d{2}-\d+',
#         ' ',
#         text
#     )

#     # remove table heading
#     text = re.sub(
#         r'.*?A\)\s*List\s+of.*?Standard\s+No\.',
#         ' ',
#         text,
#         flags=re.I | re.S
#     )

#     text = re.sub(r'\s+', ' ', text)

#     # --------------------------------------------------
#     # Split rows using serial numbers
#     # --------------------------------------------------

#     row_pattern = re.compile(
#         r'(?<!\d)(\d{1,2})\s+(.*?)(?=(?<!\d)\d{1,2}\s+|Note:|$)',
#         re.S
#     )

#     rows = row_pattern.findall(text)

#     results = []

#     # --------------------------------------------------
#     # Standard extraction
#     # --------------------------------------------------

#     std_pattern = re.compile(
#         r'('
#         r'(?:SASO|IEC)'
#         r'[\s\-_A-Z0-9]+?'
#         r'\d+(?:\s*[-]\s*\d+)?'
#         r')',
#         re.I
#     )

#     for no, row_text in rows:

#         std_match = std_pattern.search(row_text)

#         if not std_match:
#             continue

#         standard = std_match.group(1)

#         standard = re.sub(r'\s*-\s*', '-', standard)
#         standard = re.sub(r'\s+', ' ', standard).strip()

#         # --------------------------------------------------
#         # Title = everything before standard
#         # --------------------------------------------------

#         title_text = row_text[:std_match.start()]

#         english_parts = re.findall(
#             r'[A-Z][A-Za-z0-9 ,:\-\(\)/\.]+',
#             title_text
#         )

#         title = max(
#             english_parts,
#             key=len,
#             default=""
#         )

#         title = re.sub(r'\s+', ' ', title).strip()

#         results.append({
#             "no": int(no),
#             "title": title,
#             "standard": standard
#         })

#     return results

import re


def extract_standards(text):

    # --------------------------------------------------
    # Keep only Standards Section
    # --------------------------------------------------

    stop = re.search(
        r'B\)\s*(?:List\s+of\s+Products|Customs\s+Coding)',
        text,
        flags=re.I
    )

    if stop:
        text = text[:stop.start()]

    # --------------------------------------------------
    # Cleanup
    # --------------------------------------------------

    text = re.sub(
        r'Page\s+\d+\s+of\s+\d+',
        ' ',
        text,
        flags=re.I
    )

    text = re.sub(
        r'WWW\.SASO\.GOV\.SA',
        ' ',
        text,
        flags=re.I
    )

    text = re.sub(
        r'\d{2}-\d{2}-\d{2}-\d+',
        ' ',
        text
    )

    text = re.sub(
        r'.*?A\)\s*List\s+of.*?Standard\s+No\.?',
        ' ',
        text,
        flags=re.I | re.S
    )

    text = re.sub(r'\s+', ' ', text)

    # --------------------------------------------------
    # Standard Pattern
    # --------------------------------------------------

    std_pattern = re.compile(
        r'''
        (
            (?:
                SASO
                [A-Z0-9\s\-_]*?
                \d+
                (?:\s*[-]\s*\d+)?
            )
            |
            (?:
                IEC
                \s+
                \d+
                (?:\s*[-]\s*\d+)?
            )
        )
        ''',
        re.I | re.X
    )

    matches = list(std_pattern.finditer(text))

    results = []

    for idx, match in enumerate(matches):

        standard = match.group(1)

        # ----------------------------------------------
        # normalize
        # ----------------------------------------------

        standard = re.sub(
            r'(\d+)\s+(\d+)$',
            r'\1-\2',
            standard
        )

        standard = re.sub(
            r'\s*-\s*',
            '-',
            standard
        )

        standard = re.sub(
            r'\s+',
            ' ',
            standard
        ).strip()

        # ----------------------------------------------
        # previous block
        # ----------------------------------------------

        prev_end = (
            matches[idx - 1].end()
            if idx > 0
            else 0
        )

        block = text[prev_end:match.start()]

        # ----------------------------------------------
        # row number
        # ----------------------------------------------

        row_numbers = re.findall(
            r'(?<!\d)([1-7]?\d)(?!\d)',
            block
        )

        if not row_numbers:
            continue

        row_no = int(row_numbers[-1])

        # ----------------------------------------------
        # title extraction
        # ----------------------------------------------

        english_parts = re.findall(
            r'[A-Z][A-Za-z0-9 ,:\-\(\)/\.]+',
            block
        )

        title = max(
            english_parts,
            key=len,
            default=""
        )

        title = re.sub(
            r'\s+',
            ' ',
            title
        ).strip()

        title = re.sub(
            r'^\d+\s*',
            '',
            title
        )

        # remove trailing row numbers
        title = re.sub(
            r'\s+\d+$',
            '',
            title
        )

        results.append({
            "no": row_no,
            "title": title,
            "standard": standard
        })

    # --------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------

    unique = {}

    for item in results:
        key = (
            item["no"],
            item["standard"]
        )

        if key not in unique:
            unique[key] = item

    results = sorted(
        unique.values(),
        key=lambda x: x["no"]
    )

    return results