# =========================================================
# FILE: app/services/query_service.py
# =========================================================
from numpy import ma

from app.utils.response_formatter import ResponseFormatter
import json
import os

from app.utils.query_parser import extract_query_entities


class QueryService:

    # =====================================================
    # LOAD JSON
    # =====================================================

    @staticmethod
    def load_json(path):

        if not os.path.exists(path):
            return []

        with open(path, "r", encoding="utf-8") as f:

            return json.load(f)

    # =====================================================
    # SAFE STRING
    # =====================================================

    @staticmethod
    def safe_lower(value):

        if value is None:
            return ""

        return str(value).lower()

    # =====================================================
    # PRODUCT MATCH
    # =====================================================
    @staticmethod
    def normalize_text(text):

        if text is None:
            return ""

        text = str(text).lower()

        # remove special chars
        text = text.replace("-", " ")
        text = text.replace("_", " ")

        # remove extra spaces
        text = " ".join(text.split())

        return text

    @staticmethod
    def match_product(product_name, item):

        text = QueryService.normalize_text(
            json.dumps(item)
        )

        product_words = QueryService.normalize_text(
            product_name
        ).split()

        matched_words = 0

        for word in product_words:

            if word in text:

                matched_words += 1

        # ------------------------------------------------
        # MATCH SCORE
        # ------------------------------------------------

        score = matched_words / len(product_words)

        return score >= 0.7

    # =====================================================
    # MAIN ENGINE
    # =====================================================

    @staticmethod
    def process_query(query: str):

        # =================================================
        # STEP 1: UNDERSTAND QUERY
        # =================================================

        entities = extract_query_entities(query)
        
        print(f"Extracted entities: {entities}")
        # if entities

        product_name = entities.get("product_name")

        market = entities.get("market", "KSA")

        # =================================================
        # STEP 2: EMPTY RESPONSE TEMPLATE
        # =================================================

        compliance_result = {

            "query": query,

            "product": {},

            "standards": [],

            "technical_regulations": [],

            "certificates": [],

            "risk_assessment": [],

            "saber_requirements": [],

            "compliance_status": "NOT_FOUND"
        }

        # =================================================
        # STEP 3: NO PRODUCT FOUND
        # =================================================

        if not product_name:

            compliance_result["message"] = "No product identified"

            return compliance_result

        # =================================================
        # STEP 4: LOAD DATA
        # =================================================

        products = QueryService.load_json("items.json")

        standards = QueryService.load_json("std_results.json")

        technical_regulations = QueryService.load_json("tr_results.json")

        saber_rules = QueryService.load_json("saber_results.json")

        ksa_rules = QueryService.load_json("ksa_saleem.json")

        # =================================================
        # STEP 5: FIND PRODUCT
        # =================================================

        matched_product = None

        for item in products:

            if QueryService.match_product(product_name, item):

                matched_product = item

                break
        # print(f"Matched product: {matched_product}")cls
        if matched_product is None:

            compliance_result["message"] = "No matching product found in database"

            return compliance_result
        TR_NAME = matched_product.get("clause", {})
        for item in TR_NAME:
             if item.get("type", "").lower() == "Technical Regulation".lower():
                TR_NAME = item.get("value")
                break
        print(f"Extracted TR_NAME from matched product: {TR_NAME}")
        if matched_product:

            compliance_result["product"] = matched_product
        # print(f"Matched product: {matched_product}")
        

        # =================================================
        # STEP 6: FIND STANDARDS
        # =================================================

        matched_standards = []

        for item in standards:

            if QueryService.match_product(product_name, item):

                matched_standards.append(item)

        # print(f"Matched standards: {matched_standards}")

        compliance_result["standards"] = matched_standards

        # =================================================
        # STEP 7: FIND TECHNICAL REGULATIONS
        # =================================================

        matched_tr = []

        for item in technical_regulations:

            if QueryService.match_product(product_name, item):

                matched_tr.append(item)

        # print(f"Matched technical regulations: {matched_tr}")   
        compliance_result["technical_regulations"] = matched_tr

        # =================================================
        # STEP 8: FIND SABER REQUIREMENTS
        # =================================================

        matched_saber = []

        for item in saber_rules:

            if QueryService.match_product(product_name, item):

                matched_saber.append(item)
        # print(f"Matched saber requirements: {matched_saber}")

        compliance_result["saber_requirements"] = matched_saber

        # =================================================
        # STEP 9: FIND KSA SALEEM RULES
        # =================================================

        matched_ksa = []

        for item in ksa_rules:

            if QueryService.match_product(product_name, item):

                matched_ksa.append(item)

        # ADD INTO TECHNICAL REGULATIONS
        

        compliance_result["technical_regulations"].extend(matched_ksa)

        # =================================================
        # STEP 10: EXTRACT CERTIFICATES
        # =================================================

        certificates = []

        for item in matched_product.get("clause", []):

            clause_type = QueryService.safe_lower(
                item.get("type")
            )

            if "certificate" in clause_type:

                certificates.append(item)
        # print(f"Extracted certificates: {certificates}")

        compliance_result["certificates"] = certificates

        # =================================================
        # STEP 11: RISK ASSESSMENT
        # =================================================

        risks = []

        for item in matched_product.get("clause", []):

            clause_type = QueryService.safe_lower(
                item.get("type")
            )

            if "risk" in clause_type:

                risks.append(item)
        # print(f"Extracted risks: {risks}")

        compliance_result["risk_assessment"] = risks

        # =================================================
        # STEP 12: COMPLIANCE DECISION
        # =================================================

        missing = []

        if not matched_standards:
            missing.append("standards")

        if not matched_tr:
            for item in technical_regulations:
                if QueryService.match_product(TR_NAME, item):
                    matched_tr.append(item)
            if not matched_tr:
                missing.append("technical regulations")

        if not matched_saber:
            missing.append("saber requirements")

        # -------------------------------------------------

        if len(missing) == 0:

            compliance_result["compliance_status"] = "PASS"

        else:

            compliance_result["compliance_status"] = "PARTIAL"

            compliance_result["missing"] = missing

        # =================================================
        # STEP 13: FINAL RESPONSE
        # =================================================
        # formatted_response = ResponseFormatter.format_response(compliance_result)

        return compliance_result