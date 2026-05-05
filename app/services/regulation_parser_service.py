import re
from typing import Dict, List


class RegulationParserService:
    @staticmethod
    def clean_code(code):
        import re

        code = code.upper()
        code = code.replace("\n", " ")

        code = re.sub(r"\s+", " ", code)

        match = re.search(
            r"(ISO[\/\-\w]*\s*\d+(?:-\d+)?|SAE\s*J\s*\d+|SASO[\-\w\s]*\d+)",
            code
        )

        return match.group(0) if match else code.strip()

    # ---------------------------------------------------------
    @staticmethod
    def normalize_text(text):
        import re

        text = text.lower()

        # 🔥 join broken standard codes like:
        # ISO/TS \n 20100 → ISO/TS 20100
        text = re.sub(r"(iso\/ts|iso\/tr|iso)\s*\n\s*(\d+)", r"\1 \2", text)

        text = re.sub(r"(sae\s*j)\s*\n\s*(\d+)", r"\1 \2", text)

        text = re.sub(r"(saso[-\w]*)\s*\n\s*(\d+)", r"\1 \2", text)

        # remove multiple newlines
        text = re.sub(r"\n+", "\n", text)

        return text
    

    # ---------------------------------------------------------
    @staticmethod
    def extract_standards(text):
        import re

        # normalize
        text = re.sub(r"\s+", " ", text)

        # 🔥 detect rows by numbering pattern ONLY
        pattern = re.compile(
            r"\b(\d{1,3})\.\s+(.*?)"                       # full row
            r"(?=\s+\d{1,3}\.\s+|$)",                      # stop at next number
            re.IGNORECASE
        )

        matches = pattern.findall(text)

        results = []

        for num, row in matches:

            # ✅ MUST contain standard code (filter noise)
            # code_match = re.search(
            #     r"(ISO[\/\-\w\s]*\d+(?:-\d+)?|SAE\s*J\s*\d+|SASO[\-\w\s]*\d+|GSO\s*\d+|ECE\s*R\s*\d+|UN\/ECE\s*\d+)",
            #     row,
            #     re.IGNORECASE
            # )
        #     code_match = re.search(
        #     r"("
        #     r"(ISO|SAE\s*J|SASO|GSO|ECE\s*R|UN\/ECE|EN|IEC|ASTM)"
        #     r"[\-\s]*[A-Z]*[\-\s]*\d+(?:-\d+)*"
        #     r")",
        #     row,
        #     re.IGNORECASE
        # )
    #         code_match = re.search(
    #     r"""
    #     \b(
    #         # 🔹 main prefix (base + hybrids)
    #         (?:SASO[\s\-]*)?
    #         (?:ISO(?:\/TS|\/TR)?|SAE\s*J|EN|GSO|IEC|ASTM|ECE\s*R|UN\/ECE)
            
    #         # 🔹 optional chained prefixes (handles SASO-GSOEN etc.)
    #         (?:[\s\-]*(?:ISO|EN|IEC|ASTM|GSO))*
            
    #         # 🔹 main number part
    #         [\s\-]*[A-Z]?\d+
            
    #         # 🔹 optional suffix numbers (e.g., -1, -12004)
    #         (?:-\d+)*
    #     )
    #     \b
    #     """,
    #     row,
    #     re.IGNORECASE | re.VERBOSE
    # )
            code_match = re.search(
            r"""
            \b(
                (?:SASO[\s\-]*)?
                (?:ISO(?:\/TS|\/TR)?|SAE\s*J|EN|GSO|IEC|ASTM|ECE\s*R|UN\/ECE)
                (?:[\s\-]*(?:ISO|EN|IEC|ASTM|GSO))*
                [\s\-]*[A-Z]?\d+(?:-\d+)*
            )
            \b
            """,
            row,
            re.IGNORECASE | re.VERBOSE
        )



            if not code_match:
                continue   # 🚫 skip non-standard rows

            code = code_match.group(0)

            # clean code
            code = re.sub(r"[^\x00-\x7F]+", "", code).upper().strip()

            # ✅ extract LAST english part
            # eng_match = re.search(
            #     r"([a-z][a-z0-9\s\-\—\(\):,\/\.]+)$",
            #     row,
            #     re.IGNORECASE
            # )

            # if not eng_match:
            #     continue

            # title = eng_match.group(1).strip()
            segments = re.findall(
                    r"[A-Za-z][A-Za-z0-9\s\-\—\(\):,\/\.]+",
                    row
                )

            # keep only meaningful segments
            segments = [
                s.strip()
                for s in segments
                if len(s.split()) > 3   # ignore short junk
            ]

            if not segments:
                continue

            title = segments[-1]

            results.append({
                "standard_number": int(num),
                "code": code,
                "title_en": title[:50]
            })

        # remove duplicates (important for OCR)
        unique = {}
        for r in results:
            unique[r["code"]] = r

        return list(unique.values())
    # ---------------------------------------------------------
    @staticmethod
    def extract_hs_codes(text):
        import re

        pattern = re.compile(
            r"\b\d+\s+[a-z][a-z\s,()\-]+?\s+(\d{4})",
            re.IGNORECASE
        )

        matches = pattern.findall(text)

        # remove duplicates
        return [{"hs_code": code} for code in list(set(matches))]
    # ---------------------------------------------------------
    @staticmethod
    def process_regulation(text: str) -> Dict:
        """
        Main extraction function
        """
        # print("Processing regulation text (length:", len(text), ")")

        if not text or len(text) < 100:
            return {
                "total_standards": 0,
                "total_hs_codes": 0,
                "standards": [],
                "hs_codes": []
            }

        standards = RegulationParserService.extract_standards(text)
        # if len(standards) == 0:
        #     # print("No standards found, returning empty result.")
        #     return {
        #         "total_standards": 0,
        #         "total_hs_codes": 0,
        #         "standards": [],
        #         "hs_codes": []
        #     }
        hs_codes = RegulationParserService.extract_hs_codes(text)
        # print(f"Extracted {len(standards)} standards and {len(hs_codes)} HS codes" , hs_codes  )

        return {
            "total_standards": len(standards),
            "total_hs_codes": len(hs_codes),
            "standards": standards,
            "hs_codes": hs_codes
        }