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