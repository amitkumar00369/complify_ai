import re


class GenericTechnicalRequirementExtractor:

    """
    Enterprise Generic Technical Requirement Extractor

    Goal:
    Extract ONLY technical requirements
    from ANY regulation PDF/OCR text
    """

    # =====================================================
    # OBLIGATION SIGNALS
    # =====================================================

    OBLIGATION_WORDS = [

        "shall",
        "must",
        "should",
        "required",
        "ensure",
        "prevent",
        "protected",
        "installed",
        "tested",
        "designed",
        "manufactured",
        "withstand",
        "provided",
        "maintained",
        "compatible"
    ]

    # =====================================================
    # TECHNICAL SIGNALS
    # =====================================================

    TECHNICAL_WORDS = [

        "system",
        "component",
        "equipment",
        "device",
        "material",
        "pressure",
        "temperature",
        "safety",
        "leak",
        "leakage",
        "flammable",
        "corrosion",
        "fuel",
        "sensor",
        "valve",
        "hose",
        "alarm",
        "container",
        "electrical",
        "mechanical",
        "thermal",
        "installation",
        "connector",
        "gas",
        "vehicle",
        "test",
        "testing",
        "hydrogen",
        "chemical",
        "pipe",
        "storage",
        "ventilation",
        "ignition",
        "decompression",
        "heat",
        "resistance"
    ]

    # =====================================================
    # NEGATIVE / ADMIN SIGNALS
    # =====================================================

    NEGATIVE_WORDS = [

        "certificate of conformity",
        "supplier declaration",
        "official gazette",
        "market surveillance",
        "penalties",
        "violations",
        "scope",
        "definitions",
        "wto",
        "regulatory authority",
        "withdrawal",
        "recall",
        "commercial fraud",
        "type approval",
        "publication",
        "appeal",
        "minister",
        "hs code",
        "customs",
        "import license",
        "economic operators"
    ]

    # =====================================================
    # INIT
    # =====================================================

    def __init__(self, text):

        self.raw_text = text

        self.text = self.normalize(text)

    # =====================================================
    # NORMALIZE
    # =====================================================

    def normalize(self, text):

        text = text.replace("\r", "\n")

        # remove extra spaces
        text = re.sub(
            r"[ \t]+",
            " ",
            text
        )

        # normalize new lines
        text = re.sub(
            r"\n{2,}",
            "\n",
            text
        )

        # remove page numbers
        text = re.sub(
            r"Page\s+\d+\s+(of|from)\s+\d+",
            "",
            text,
            flags=re.IGNORECASE
        )

        # remove repeated TR IDs
        text = re.sub(
            r"\b\d{2}-\d{2}-\d{2}-\d{2}-\d{3}\b",
            "",
            text
        )

        return text.strip()

    # =====================================================
    # SPLIT SENTENCES
    # =====================================================

    def split_sentences(self):

        text = self.text.replace("\n", " ")

        sentences = re.split(

            r'(?<=[.!?])\s+',

            text
        )

        cleaned = []

        for sentence in sentences:

            sentence = sentence.strip()

            if len(sentence) < 25:
                continue

            cleaned.append(sentence)

        return cleaned

    # =====================================================
    # VALID TECHNICAL REQUIREMENT
    # =====================================================

    def is_technical_requirement(self, sentence):

        lower = sentence.lower()

        # -------------------------------------------------
        # REMOVE DEFINITIONS
        # -------------------------------------------------

        if (
            "means" in lower
            or "defined as" in lower
        ):
            return False

        # -------------------------------------------------
        # REMOVE OBJECTIVES
        # -------------------------------------------------

        if (
            "aims to" in lower
            or "this regulation" in lower
        ):
            return False

        # -------------------------------------------------
        # REMOVE ADMIN / LEGAL
        # -------------------------------------------------

        if any(
            word in lower
            for word in self.NEGATIVE_WORDS
        ):
            return False

        # -------------------------------------------------
        # REMOVE ARTICLE HEADINGS
        # -------------------------------------------------

        if re.match(
            r'^article\s*\(\d+\)',
            lower
        ):
            return False

        # -------------------------------------------------
        # REMOVE TOC / INDEX LINES
        # -------------------------------------------------

        if re.match(
            r'^\d+\s+[A-Z]',
            sentence
        ):
            return False

        # -------------------------------------------------
        # REMOVE ANNEX HEADINGS
        # -------------------------------------------------

        if "annex" in lower and len(sentence.split()) < 15:
            return False

        # -------------------------------------------------
        # MUST HAVE OBLIGATION WORD
        # -------------------------------------------------

        has_obligation = any(

            word in lower

            for word in
            self.OBLIGATION_WORDS
        )

        if not has_obligation:
            return False

        # -------------------------------------------------
        # MUST HAVE TECHNICAL CONTEXT
        # -------------------------------------------------

        technical_count = sum(

            1 for word
            in self.TECHNICAL_WORDS

            if word in lower
        )

        if technical_count < 2:
            return False

        # -------------------------------------------------
        # REMOVE VERY SHORT TEXT
        # -------------------------------------------------

        if len(sentence.split()) < 8:
            return False

        return True

    # =====================================================
    # CLEAN SENTENCE
    # =====================================================

    def clean(self, text):

        # remove extra spaces
        text = re.sub(
            r"\s+",
            " ",
            text
        )

        # remove OCR bullets
        text = re.sub(
            r"[•▪■□]",
            "",
            text
        )

        return text.strip()

    # =====================================================
    # MAIN EXTRACTION
    # =====================================================

    def extract(self):

        results = []

        seen = set()

        sentences = self.split_sentences()

        for sentence in sentences:

            if self.is_technical_requirement(
                sentence
            ):

                clean = self.clean(sentence)

                # deduplicate
                key = clean[:200]

                if key not in seen:

                    seen.add(key)

                    results.append(clean)

        return {

            "technical_requirements":
                results
        }


# =========================================================
# USAGE
# =========================================================


def extract_technical_requirements(reg_text: str) -> str:
    """
    Extract the '4/2 – Technical Requirements' section from the SASO Hydrogen Vehicles regulation.
    """
    # Pattern matches the heading "4/2 – Technical Requirements" (allows optional spaces/hyphens)
    # Then captures everything until:
    #   - a line starting with "4/3" (next clause), or
    #   - a line starting with "Article (5)" (next article), or
    #   - end of string.
    pattern = r'(4/2\s*[–-]\s*Technical Requirements.*?)(?=\n\s*(?:4/3|Article\s*\(5\))|\Z)'
    match = re.search(pattern, reg_text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""

# Example usage with your data (assuming it's in a variable)
# For demonstration, I'll load the string from the provided JSON field.
data = {
    "reqqqq": "01-02-07-22-183 Saudi Standards Organization The page 1 ... (the full text you gave) ..."
}

regulation_text = data["reqqqq"]
extracted = extract_technical_requirements(regulation_text)
print(extracted)


import re


# def extract_toc(text):

#     pattern = re.compile(
#         r"""
#         (
#             Preamble
#             |
#             Article\s*\(\d+\)\s*.*?
#             |
#             Annex\s*\([^)]+\)\s*.*?
#         )
#         \s*
#         \.{2,}
#         \s*
#         (\d+)
#         """,
#         re.VERBOSE | re.IGNORECASE
#     )

#     matches = pattern.findall(text)

#     toc = []

#     for match in matches:

#         title = match[0].strip()

#         page = int(match[1])

#         # clean article numbering
#         title = re.sub(
#             r"Article\s*\(\d+\)",
#             "",
#             title,
#             flags=re.IGNORECASE
#         ).strip()

#         # clean annex numbering
#         title = re.sub(
#             r"Annex\s*\([^)]+\)",
#             "",
#             title,
#             flags=re.IGNORECASE
#         ).strip()

#         toc.append({
#             "section": title,
#             "start_page": page
#         })

#     # --------------------------------------
#     # CALCULATE END PAGE
#     # --------------------------------------

#     for i in range(len(toc)):

#         if i < len(toc) - 1:

#             toc[i]["end_page"] = (
#                 toc[i + 1]["start_page"]
#             )

#         else:

#             toc[i]["end_page"] = None

#     return toc


# # ==========================================
# # TEST
# # ==========================================

import re


def clean_page_number(page_text):

    page_text = page_text.strip()

    # OCR fixes
    page_text = page_text.replace("I ", "1")
    page_text = page_text.replace("II", "11")
    page_text = page_text.replace("I0", "10")
    page_text = page_text.replace("l0", "10")

    # keep digits only
    page_text = re.sub(r"[^\d]", "", page_text)

    if not page_text:
        return None

    return int(page_text)


def extract_toc(text):
    print(text[:2000])

    # ---------------------------------------------------
    # SPLIT USING ARTICLE / ANNEX BOUNDARIES
    # ---------------------------------------------------

    pattern = re.compile(
        r"""
        (
            Preamble
            |
            Article\s*\(\s*\d+\s*\).*?
            |
            Annex\s*(?:No\.)?\s*\([^)]+\).*?
        )
        \.{2,}
        \s*
        ([\dI l]+)
        """,
        re.VERBOSE | re.IGNORECASE
    )

    matches = pattern.findall(text)

    toc = []

    for match in matches:

        raw_title = match[0].strip()

        raw_page = match[1].strip()

        page = clean_page_number(raw_page)
        page = clean_page_number(raw_page)



# prevent OCR merged garbage
        if not page:
                    continue
        if page > 100:
            page = int(str(page)[:2])

        

        # -------------------------------------------
        # CLEAN SECTION TITLE
        # -------------------------------------------

        title = re.sub(
            r"Article\s*\(\s*\d+\s*\)\s*[:]?",
            "",
            raw_title,
            flags=re.IGNORECASE
        ).strip()

        title = re.sub(
            r"Annex\s*(?:No\.)?\s*\([^)]+\)",
            "",
            title,
            flags=re.IGNORECASE
        ).strip()

        title = re.sub(r"\s+", " ", title)

        toc.append({
            "section": title,
            "start_page": page
        })

    # ---------------------------------------------------
    # END PAGE
    # ---------------------------------------------------

    for i in range(len(toc)):

        if i < len(toc) - 1:

            toc[i]["end_page"] = (
                toc[i + 1]["start_page"]
            )

        else:

            toc[i]["end_page"] = None

    return toc


import re


def clean_text(text: str):

    text = re.sub(r'\s+', ' ', text)

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

    # ---------------------------------------
    # HANDLE:
    # 4/111 -> 4/1/1
    # ---------------------------------------

    if re.match(r'^\d+/\d{3}$', clause):

        main, digits = clause.split('/')

        clause = (
            f"{main}/{digits[0]}/{digits[1:]}"
        )

    return clause


# ---------------------------------------------------
# RECONSTRUCT OCR STRUCTURE
# ---------------------------------------------------

def reconstruct_structure(text):

    # newline before:
    # 4/111
    # 4/1/1
    # 4.1.1
    # 4-1-1

    text = re.sub(
        r'(\s)(\d+(?:[\/\.\-]\d+)+)',
        r'\n\2',
        text
    )

    # newline before Article
    text = re.sub(
        r'(Article\s*\(\s*\d+\s*\))',
        r'\n\1',
        text
    )

    return text.strip()

def extract_tr_code(text):

    match = re.search(
        r'\b\d{2}-\d{2}-\d{2}-\d+\b',
        text
    )

    if match:
        return match.group(0)

    return None
# ---------------------------------------------------
# ARTICLE EXTRACTION
# ---------------------------------------------------

def extract_article_block(
    text,
    start_texts=None,
    end_article="5"
):

    if start_texts is None:

        start_texts = [
            "Obligations of Supplier",
            "Supplier's Obligations",
            "Suppliers Obligations",
            "Obligations of the Supplier",
            "Article (4)"
        ]

    start_index = None

    for start_text in start_texts:

        start_match = re.search(
            re.escape(start_text),
            text,
            flags=re.I
        )

        if start_match:

            start_index = start_match.start()

            break

    if start_index is None:
        return ""

    end_match = re.search(
        rf'Article\s*\(\s*{end_article}\s*\)',
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

def extract_regulation_structure(text):

    # ---------------------------------------
    # CLEAN
    # ---------------------------------------
    tr_code = extract_tr_code(text)
    print(tr_code)
    text = clean_text(text)

    # ---------------------------------------
    # ARTICLE BLOCK
    # ---------------------------------------

    text = extract_article_block(text)
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
        r'\b\d{2}-\d{2}-\d{2}-\d+\b',
        '',
        text
    )

    # ---------------------------------------
    # REBUILD OCR STRUCTURE
    # ---------------------------------------

    text = reconstruct_structure(text)
    

    # ---------------------------------------
    # MAIN SECTION REGEX
    #
    # 4/1
    # 4.1
    # 4-1
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

        full_section_text = (
            section.group(2).strip()
        )

        # -----------------------------------
        # TITLE EXTRACTION
        # -----------------------------------

        title_match = re.match(
        r'^([A-Za-z\s]+?requirements)\b',
        full_section_text,
        flags=re.I
    )

        if title_match:

            section_title = (
                title_match.group(1).strip()
            )

            remaining_intro = (
                full_section_text[
                    title_match.end():
                ].strip()
            )

        else:

            section_title = full_section_text
            remaining_intro = ""

        start = section.end()

        if idx + 1 < len(sections):
            end = sections[idx + 1].start()
        else:
            end = len(text)

        section_body = text[start:end].strip()

        lines = section_body.split("\n")

        intro_lines = []

        if remaining_intro:
            intro_lines.append(
                remaining_intro
            )

        # -----------------------------------
        # GENERIC CHILD REGEX
        #
        # 4/111
        # 4/1/1
        # 4.1.1
        # 4-1-1
        # -----------------------------------

        child_pattern = re.compile(
            r'^(\d+(?:[\/\.\-]\d+)+)\s+(.*)$'
        )

        items = {}

        current_child = None

        current_content = []

        before_child = True

        for line in lines:

            line = line.strip()

            if not line:
                continue

            child_match = child_pattern.match(
                line
            )

            if child_match:

                before_child = False

                # save previous child
                if current_child:

                    items[current_child] = (
                        " ".join(current_content)
                        .strip()
                    )

                raw_child_key = (
                    child_match.group(1)
                )

                normalized_child = (
                    normalize_clause_number(
                        raw_child_key
                    )
                )

                current_child = normalized_child

                current_content = [
                    child_match.group(2)
                ]

            else:

                if before_child:

                    intro_lines.append(line)

                else:

                    current_content.append(line)

        # save last child
        if current_child:

            items[current_child] = (
                " ".join(current_content)
                .strip()
            )

        result[section_key] = {
            "title": section_title,
            "intro": " ".join(
                intro_lines
            ).strip(),
            "items": items
        }

    return result,tr_rq,tr_code