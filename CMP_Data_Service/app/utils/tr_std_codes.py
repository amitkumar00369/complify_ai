import re


def extract_standards(text):

    # ----------------------------------
    # Remove unwanted sections
    # ----------------------------------

    stop = re.search(
        r'B\)\s*List\s+of\s+Products\s+and\s+Customs\s+Coding',
        text,
        flags=re.I
    )

    if stop:
        text = text[:stop.start()]

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

    text = re.sub(r'\s+', ' ', text)

    # ----------------------------------
    # Standard pattern
    # ----------------------------------

    std_pattern = re.compile(
        r'SASO[- ]?(?:ISO|IEC|ASTM|GSO)[- ]?[A-Z0-9\- ]+?(?=\s+\d+\s+|Note:|$)',
        re.I
    )

    matches = list(std_pattern.finditer(text))

    results = []

    for idx, match in enumerate(matches):

        standard = match.group().strip()

        standard = re.sub(r'\s+', ' ', standard)

        # remove OCR garbage
        standard = re.sub(r'\s+Note$', '', standard, flags=re.I)

        block_start = (
            matches[idx - 1].end()
            if idx > 0
            else 0
        )

        block_end = match.start()

        block = text[block_start:block_end]

        # serial number
        serials = re.findall(r'\b(\d{1,2})\b', block)

        no = None

        if serials:
            no = int(serials[-1])

        # English title only
        english_sentences = re.findall(
            r'[A-Z][A-Za-z0-9 ,:\-\(\)/\.]+',
            block
        )

        title = max(
            english_sentences,
            key=len,
            default=""
        )

        title = re.sub(r'\s+', ' ', title).strip()

        results.append({
            "no": no,
            "standard": standard,
            "title": title
        })
        for idx, item in enumerate(results, start=1):

            item["no"] = idx

            item["standard"] = re.sub(
                r'\s+',
                ' ',
                item["standard"]
            ).strip()

            item["standard"] = re.sub(
                r'(\d+-)\s+(\d+)',
                r'\1\2',
                item["standard"]
            )

    return results