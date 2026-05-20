import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

# ============================================================
# LEGAL CLAUSE OBJECT
# ============================================================

@dataclass
class LegalClause:
    article: Optional[str]
    clause_id: Optional[str]
    subclause: Optional[str]
    section_title: Optional[str]
    annex: Optional[str]
    obligation_level: str
    validation_types: List[str]
    text: str


# ============================================================
# LEGAL STRUCTURE PARSER
# ============================================================

class LegalStructureParser:

    MANDATORY_WORDS = [
        "shall",
        "must",
        "required",
        "shall not",
        "may",
        "should"
    ]

    SKIP_SECTIONS = [
        "terms and definitions",
        "definitions",
        "references",
        "scope",
        "foreword",
        "table of contents",
    ]

    VALIDATION_MAP = {
        "testing_validation": [
            "test",
            "testing",
            "inspection",
            "evaluation",
            "verified",
        ],

        "safety_validation": [
            "safety",
            "hazard",
            "flammable",
            "protection",
            "danger",
        ],

        "conformity_validation": [
            "conformity",
            "compliance",
            "certificate",
            "approval",
            "regulation",
        ],

        "technical_validation": [
            "pressure",
            "temperature",
            "leakage",
            "hydrogen system",
            "container",
            "valve",
            "installation",
        ],

        "documentation_validation": [
            "technical documentation",
            "technical file",
            "documents",
            "dossier",
            "reports",
        ],

        "supplier_validation": [
            "supplier",
            "manufacturer",
            "importer",
            "notified body",
        ],

        "risk_validation": [
            "risk",
            "hazard",
            "assessment",
        ]
    }

    # ========================================================
    # CLEAN TEXT
    # ========================================================

    def clean_text(self, text: str):

        text = text.replace("\x00", " ")

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # ========================================================
    # REMOVE METADATA / PAGE NOISE
    # ========================================================

    def remove_noise(self, text: str):

        lines = text.split("\n")

        cleaned = []

        for line in lines:

            line = line.strip()

            if not line:
                continue

            # remove page numbers
            if re.search(r"Page\s+\d+\s+from\s+\d+", line):
                continue

            # remove standards references
            if re.match(
                r"^(ISO|IEC|SASO|GSO|ASTM|EN|UN/ECE|ECE)\b",
                line,
                re.IGNORECASE
            ):
                continue

            # remove toc lines
            if re.search(r"\.{5,}", line):
                continue

            cleaned.append(line)

        return "\n".join(cleaned)

    # ========================================================
    # SPLIT INTO STRUCTURED BLOCKS
    # ========================================================

    def build_legal_blocks(self, text: str):

        """
        Build legal blocks using:
        Article (x)
        4/1
        4/1/2
        A)
        B)
        """

        pattern = re.compile(
            r"""
            (
                Article\s*\(\d+\)
                |
                \d+/\d+/\d+
                |
                \d+/\d+
                |
                [A-Z]\)
            )
            """,
            re.VERBOSE
        )

        matches = list(pattern.finditer(text))

        blocks = []

        for i in range(len(matches)):

            start = matches[i].start()

            end = (
                matches[i + 1].start()
                if i + 1 < len(matches)
                else len(text)
            )

            block = text[start:end].strip()

            blocks.append(block)

        return blocks

    # ========================================================
    # ARTICLE EXTRACTION
    # ========================================================

    def extract_article(self, block: str):

        article_match = re.search(
            r"Article\s*\((\d+)\)",
            block,
            re.IGNORECASE
        )

        if article_match:
            return article_match.group(1)

        clause_match = re.search(
            r"\b(\d+/\d+/\d+|\d+/\d+)\b",
            block
        )

        if clause_match:
            return clause_match.group(1)

        return None

    # ========================================================
    # SUBCLAUSE EXTRACTION
    # ========================================================

    def extract_subclause(self, block: str):

        match = re.search(r"\b([A-Z])\)", block)

        if match:
            return match.group(1)

        return None

    # ========================================================
    # ANNEX EXTRACTION
    # ========================================================

    def extract_annex(self, block: str):

        match = re.search(
            r"Annex\s*\(?(\d+)\)?",
            block,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

        return None

    # ========================================================
    # OBLIGATION LEVEL
    # ========================================================

    def detect_obligation(self, text: str):

        lower = text.lower()

        if "shall not" in lower:
            return "prohibited"

        if "shall" in lower:
            return "mandatory"

        if "must" in lower:
            return "mandatory"

        if "required" in lower:
            return "mandatory"

        if "should" in lower:
            return "recommended"

        if "may" in lower:
            return "optional"

        return "informational"

    # ========================================================
    # VALIDATION CLASSIFIER
    # ========================================================

    def classify_validation(self, text: str):

        lower = text.lower()

        categories = []

        for category, keywords in self.VALIDATION_MAP.items():

            if any(k in lower for k in keywords):

                categories.append(category)

        return list(set(categories))

    # ========================================================
    # SKIP NON-REGULATORY CONTENT
    # ========================================================

    def should_skip(self, block: str):

        lower = block.lower()

        # definitions section
        if any(section in lower for section in self.SKIP_SECTIONS):
            return True

        # too short
        if len(block) < 40:
            return True

        # no obligation language
        if not any(
            word in lower
            for word in self.MANDATORY_WORDS
        ):
            return True

        # standard references only
        if re.match(
            r"^(ISO|IEC|SASO|GSO|ASTM|EN|UN/ECE)",
            block,
            re.IGNORECASE
        ):
            return True

        return False

    # ========================================================
    # MAIN PARSER
    # ========================================================

    def parse(self, text: str):

        # text = self.clean_text(text)

        # text = self.remove_noise(text)

        blocks = self.build_legal_blocks(text)

        extracted = []

        seen = set()

        current_article = None

        for block in blocks:

            if self.should_skip(block):
                continue

            article = self.extract_article(block)

            if article:
                current_article = article

            else:
                article = current_article

            normalized = re.sub(
                r"\s+",
                " ",
                block.lower()
            )

            if normalized in seen:
                continue

            seen.add(normalized)

            clause = LegalClause(

                article=article,

                clause_id=article,

                subclause=self.extract_subclause(block),

                section_title=None,

                annex=self.extract_annex(block),

                obligation_level=self.detect_obligation(block),

                validation_types=self.classify_validation(block),

                text=block
            )

            extracted.append(asdict(clause))

        return extracted


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":

    parser = LegalStructureParser()

    with open("Pasted text(185).txt", "r", encoding="utf-8") as f:
        raw_text = f.read()

    clauses = parser.parse(raw_text)

    print("=" * 100)
    print("TOTAL CLAUSES:", len(clauses))
    print("=" * 100)

    for item in clauses[:20]:

        print("\n")
        print("-" * 80)

        print("ARTICLE:", item["article"])
        print("SUBCLAUSE:", item["subclause"])
        print("ANNEX:", item["annex"])
        print("OBLIGATION:", item["obligation_level"])
        print("VALIDATIONS:", item["validation_types"])

        print("\nTEXT:")
        print(item["text"])