import re


# ------------------------------------------------
# CLEAN PAGE NUMBER
# ------------------------------------------------

def clean_page_number(page_text):

    if not page_text:
        return None

    page_text = page_text.strip()

    replacements = {
        "I": "1",
        "l": "1",
        "O": "0",
        "o": "0"
    }

    for old, new in replacements.items():
        page_text = page_text.replace(old, new)

    page_text = re.sub(r"[^\d]", "", page_text)

    if not page_text:
        return None

    try:
        return int(page_text)
    except:
        return None


# ------------------------------------------------
# CLEAN TITLE
# ------------------------------------------------

def clean_section_title(title):

    if not title:
        return ""

    title = title.strip()

    # remove dots
    title = re.sub(r"\.{2,}", "", title)

    # normalize spaces
    title = re.sub(r"\s+", " ", title)

    # OCR fixes
    replacements = {
        "(I)": "(1)",
        "(II)": "(11)",
        "( l )": "(1)",
        "( l)": "(1)",
        "ARTICLE I": "ARTICLE 1",
        "AnnexNo.": "Annex No.",
        "(1- A)": "(1-A)",
        "(1- B)": "(1-B)"
    }

    for old, new in replacements.items():
        title = title.replace(old, new)

    return title.strip()


# ------------------------------------------------
# INSERT NEWLINES BEFORE TOC KEYWORDS
# ------------------------------------------------

def insert_virtual_newlines(text):

    keywords = [
        "INTRODUCTION",
        "CHAPTER",
        "GENERAL PROVISIONS",
        "FINAL AND TRANSITIONAL PROVISIONS",
        "CONFORMITY ASSESSMENT",
        "OBLIGATIONS",
        "ADMINISTRATIVE PROVISIONS",
        "ARTICLE",
        "ANNEX",
        "PREAMBLE"
    ]

    pattern = r"\s+(?=(" + "|".join(keywords) + r")\b)"

    text = re.sub(
        pattern,
        "\n",
        text,
        flags=re.IGNORECASE
    )

    return text


# ------------------------------------------------
# CHECK IF TOC LINE
# ------------------------------------------------

def is_toc_line(line):

    line_upper = line.upper()

    keywords = [
        "INTRODUCTION",
        "CHAPTER",
        "ARTICLE",
        "ANNEX",
        "PREAMBLE",
        "GENERAL PROVISIONS",
        "FINAL PROVISIONS",
        "CONFORMITY",
        "OBLIGATIONS",
        "ADMINISTRATIVE"
    ]

    has_keyword = any(
        keyword in line_upper
        for keyword in keywords
    )

    has_page_number = bool(
        re.search(r"[IlOol\d\s]{1,6}\s*$", line)
    )

    # reject page headers
    if re.search(
        r'GSO\s+\d+\s*/\s*\d+',
        line,
        re.IGNORECASE
    ):
        return False

    # reject body text
    bad_phrases = [
        "WORLD TRADE ORGANIZATION",
        "IN ACCORDANCE WITH",
        "COUNCIL OF MINISTERS",
        "TECHNICAL BARRIERS",
        "STATUTE OF"
    ]

    has_bad_phrase = any(
        phrase in line_upper
        for phrase in bad_phrases
    )

    if has_bad_phrase:
        return False

    if len(line) > 500:
        return False

    return has_keyword and has_page_number


# ------------------------------------------------
# EXTRACT TITLE + PAGE
# ------------------------------------------------

def extract_title_and_page(line):

    line = re.sub(r"\s+", " ", line).strip()

    # page at end
    page_match = re.search(
        r"([IlOol\d]+)\s*$",
        line
    )

    if not page_match:
        return None, None

    page = clean_page_number(
        page_match.group(1)
    )

    if not page:
        return None, None

    title = line[:page_match.start()].strip()

    title = re.sub(
        r"\.{2,}",
        "",
        title
    )

    title = clean_section_title(title)

    return title, page


# ------------------------------------------------
# MERGE WRAPPED LINES
# ------------------------------------------------

def merge_wrapped_lines(lines):

    merged = []

    buffer = ""

    for line in lines:

        line = line.strip()

        if not line:
            continue

        line = re.sub(r"\s+", " ", line)

        # ends with page number
        if re.search(r"[IlOol\d]+\s*$", line):

            if buffer:
                line = buffer + " " + line
                buffer = ""

            merged.append(line)

        else:
            buffer += " " + line

    if buffer:
        merged.append(buffer)

    return merged


# ------------------------------------------------
# MAIN TOC EXTRACTOR
# ------------------------------------------------
def clean_table_of_contents(table_of_contents):
    # print("Cleaning TOC entries...",table_of_contents)
    cleaned_toc = []

    seen_annex = False

    for item in table_of_contents:

        section = item["section"].strip()

        # Valid TOC entries
        is_article = re.match(r"^Article\s*\(\d+\)", section, re.I)
        is_annex = re.match(r"^Annex\s*\(", section, re.I)
        is_preamble = section.lower() == "preamble"

        if is_annex:
            seen_annex = True
            cleaned_toc.append(item)
            continue

        if is_article:

            # After annexes, article entries are usually OCR/body-text noise
            if seen_annex:
                print(f"Stopping TOC at: {section}")
                break

            cleaned_toc.append(item)
            continue

        if is_preamble and not seen_annex:
            cleaned_toc.append(item)
def extract_toc(text):
    # print(text)

    # ------------------------------------------------
    # NORMALIZE
    # ------------------------------------------------

    text = text.replace("\r", "\n")

    text = re.sub(r"[ \t]+", " ", text)

    # ------------------------------------------------
    # INSERT VIRTUAL NEWLINES
    # ------------------------------------------------

    text = insert_virtual_newlines(text)

    # ------------------------------------------------
    # SPLIT LINES
    # ------------------------------------------------

    lines = text.split("\n")

    # ------------------------------------------------
    # MERGE WRAPPED LINES
    # ------------------------------------------------

    lines = merge_wrapped_lines(lines)

    toc = []

    # ------------------------------------------------
    # PROCESS
    # ------------------------------------------------

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if not is_toc_line(line):
            continue

        title, page = extract_title_and_page(line)

        if not title or not page:
            continue

        toc.append({
            "section": title,
            "start_page": page
        })

    # ------------------------------------------------
    # REMOVE DUPLICATES
    # ------------------------------------------------

    unique = []

    seen = set()

    for item in toc:

        key = (
            item["section"],
            item["start_page"]
        )

        if key not in seen:

            seen.add(key)

            unique.append(item)

    toc = unique

    # ------------------------------------------------
    # SORT BY PAGE
    # ------------------------------------------------

    toc = sorted(
        toc,
        key=lambda x: x["start_page"]
    )

    # ------------------------------------------------
    # GENERATE END PAGE
    # ------------------------------------------------

    for i in range(len(toc)):

        if i < len(toc) - 1:

            toc[i]["end_page"] = (
                toc[i + 1]["start_page"]
            )

        else:

            toc[i]["end_page"] = None

    return toc