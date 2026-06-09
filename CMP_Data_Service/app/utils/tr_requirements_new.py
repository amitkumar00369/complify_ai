import re


# ---------------------------------------------------
# CLEAN TEXT
# ---------------------------------------------------

def clean_text(text: str):

    # preserve structure/newlines
    text = re.sub(
        r'[ \t]+',
        ' ',
        text
    )

    # normalize blank lines
    text = re.sub(
        r'\n{3,}',
        '\n\n',
        text
    )

    replacements = {
        "sup pi ier": "supplier",
        "product s": "product's",
        "System ofUnits": "System of Units",
        "fu lfil": "fulfil",
        "ofthe": "of the",
        "tfl": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.strip()


# ---------------------------------------------------
# NORMALIZE CLAUSE NUMBERING
# ---------------------------------------------------

def normalize_clause_number(clause):

    # 4.1.1 -> 4/1/1
    clause = clause.replace(".", "/")

    # 4-1-1 -> 4/1/1
    clause = clause.replace("-", "/")

    # 4/111 -> 4/1/1
    if re.match(r'^\d+/\d{3}$', clause):

        main, digits = clause.split('/')

        clause = (
            f"{main}/{digits[0]}/{digits[1:]}"
        )

    return clause


# ---------------------------------------------------
# RECONSTRUCT STRUCTURE
# ---------------------------------------------------

def reconstruct_structure(text):

    # -----------------------------------
    # ARTICLE HEADERS
    # -----------------------------------

    text = re.sub(
        r'(Article\s*\(\s*\d+\s*\))',
        r'\n\1',
        text
    )

    # -----------------------------------
    # MAIN CLAUSES
    # 4/1
    # 4.1
    # -----------------------------------

    text = re.sub(
        r'\s(\d+[\/\.\-]\d+)\s+([A-Z])',
        r'\n\1 \2',
        text
    )

    # -----------------------------------
    # SUB CLAUSES
    # 4/1/1
    # 4.1.1
    # -----------------------------------

    text = re.sub(
        r'\s(\d+(?:[\/\.\-]\d+){2,})',
        r'\n\1',
        text
    )

    # -----------------------------------
    # A) B) C)
    # -----------------------------------

    text = re.sub(
        r'\s([A-Z]\))',
        r'\n\1',
        text
    )

    # -----------------------------------
    # BULLETS
    # -----------------------------------

    text = re.sub(
        r'\s([•▪■])',
        r'\n\1',
        text
    )

    # -----------------------------------
    # NEWLINE AFTER SECTION TITLES
    # -----------------------------------

    text = re.sub(
        r'(\d+[\/\.\-]\d+\s+[A-Z][A-Za-z\s]+)\s+(It|The|In|International|Products)',
        r'\1\n\2',
        text
    )

    # -----------------------------------
    # REMOVE EXTRA BLANK LINES
    # -----------------------------------

    text = re.sub(
        r'\n{3,}',
        '\n\n',
        text
    )

    return text.strip()


# ---------------------------------------------------
# EXTRACT TR CODE
# ---------------------------------------------------

def extract_tr_code(text):

    match = re.search(
        r'\b\d{2}-\d{2}-\d{2}-\d+\b',
        text
    )

    if match:
        return match.group(0)

    return None


# ---------------------------------------------------
# EXTRACT ARTICLE BLOCK
# ---------------------------------------------------

def extract_article_block(
    text,
    text_scope
):
    

    

    start_match = re.search(
            re.escape(text_scope.get("start")),
            text,
            flags=re.I
        )
    start_index = 0

    if start_match:

        start_index = start_match.start()
      



    end_match = re.search(
        rf'Article\s*\(\s*{text_scope.get("end")}\s*\)',
        text,
        flags=re.I
    )

    if end_match:
        end_index = end_match.start()
    else:
        end_index = len(text)

    return text[start_index:end_index]


# ---------------------------------------------------
# MAIN PARSER
# ---------------------------------------------------

def extract_regulation_structures(text,text_scope=None):

    # ---------------------------------------
    # CLEAN
    # ---------------------------------------

    tr_code = extract_tr_code(text)

    text = clean_text(text)

    # ---------------------------------------
    # ARTICLE BLOCK
    # ---------------------------------------
    if text_scope is not None:
        text = extract_article_block(text,text_scope)

    tr_rq = text

    # ---------------------------------------
    # REMOVE PAGE GARBAGE
    # ---------------------------------------

    text = re.sub(
        r'Page\s+\d+\s+of\s+\d+',
        '',
        text,
        flags=re.I
    )

    text = re.sub(
        r'WWW\.SASO\.GOV\.SA',
        '',
        text,
        flags=re.I
    )

    text = re.sub(
        r'\b\d{2}-\d{2}-\d{2}-\d+\b',
        '',
        text
    )

    # ---------------------------------------
    # REBUILD STRUCTURE
    # ---------------------------------------

    text = reconstruct_structure(text)

    # ---------------------------------------
    # SECTION REGEX
    # ---------------------------------------

    section_pattern = re.compile(
        r'^(\d+[\/\.\-]\d+)\s+([^\n]+)',
        re.MULTILINE
    )

    sections = list(
        section_pattern.finditer(text)
    )

    result = {}

    # ---------------------------------------
    # LOOP SECTIONS
    # ---------------------------------------

    for idx, section in enumerate(sections):

        raw_section_key = (
            section.group(1).strip()
        )

        section_key = normalize_clause_number(
            raw_section_key
        )

        section_title = (
            section.group(2)
            .strip()
        )

        start = section.end()

        if idx + 1 < len(sections):
            end = sections[idx + 1].start()
        else:
            end = len(text)

        section_body = text[start:end].strip()

        lines = section_body.split("\n")

        intro_lines = []

        # -----------------------------------
        # NUMERIC CHILD CLAUSES
        # -----------------------------------

        child_pattern = re.compile(
            r'^(\d+(?:[\/\.\-]\d+)+)\s+(.*)$'
        )

        # -----------------------------------
        # ALPHA CLAUSES
        # A)
        # B)
        # -----------------------------------

        alpha_pattern = re.compile(
            r'^([A-Z])\)\s+(.*)$'
        )

        items = {}

        current_child = None

        current_content = []

        before_child = True

        # -----------------------------------
        # LOOP BODY LINES
        # -----------------------------------

        for line in lines:

            line = line.strip()

            if not line:
                continue

            child_match = child_pattern.match(
                line
            )

            alpha_match = alpha_pattern.match(
                line
            )

            # -----------------------------------
            # NEW CHILD CLAUSE
            # -----------------------------------

            if child_match or alpha_match:

                before_child = False

                # save previous child
                if current_child:

                    items[current_child] = (
                        " ".join(current_content)
                        .strip()
                    )

                # -------------------------------
                # NUMERIC CHILD
                # -------------------------------

                if child_match:

                    raw_child_key = (
                        child_match.group(1)
                    )

                    normalized_child = (
                        normalize_clause_number(
                            raw_child_key
                        )
                    )

                    current_content = [
                        child_match.group(2)
                    ]

                # -------------------------------
                # ALPHA CHILD
                # -------------------------------

                else:

                    alpha_key = (
                        alpha_match.group(1)
                    )

                    normalized_child = (
                        f"{section_key}/{alpha_key}"
                    )

                    current_content = [
                        alpha_match.group(2)
                    ]

                current_child = normalized_child

            # -----------------------------------
            # NORMAL CONTENT
            # -----------------------------------

            else:

                if before_child:

                    intro_lines.append(line)

                else:

                    current_content.append(line)

        # -----------------------------------
        # SAVE LAST CHILD
        # -----------------------------------

        if current_child:

            items[current_child] = (
                " ".join(current_content)
                .strip()
            )

        # -----------------------------------
        # FINAL INTRO
        # -----------------------------------

        final_intro = " ".join(
            intro_lines
        ).strip()

        # -----------------------------------
        # FINAL OBJECT
        # -----------------------------------

        result[section_key] = {
            "title": section_title,
            "intro": final_intro,
            "items": items
        }

    return {
        "tr_code": tr_code,
        "req_raw_data": tr_rq,
        "tr_requirement": result
    }