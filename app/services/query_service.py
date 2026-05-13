# # =========================================================
# # FILE: app/services/query_service.py
# # =========================================================

# from numpy import ma

# # from app.services.llama_service import answerWithQuery
# from app.utils.HsCodeRegex import HSCodeService
# from app.utils.intent_result_builder import handle_query
# from app.utils.intententResponse.detailsResponse import build_compliance_response
# from app.utils.responseBuilder import ComplianceResponseBuilder
# from app.utils.response_formatter import ResponseFormatter
# import json
# import os

# from app.utils.query_parser import extract_query_entities, extract_query_entities_extended
# from app.utils.text_cleaner import TextCleaner


# class QueryService:

#     # =====================================================
#     # LOAD JSON
#     # =====================================================

#     @staticmethod
#     def load_json(path):

#         if not os.path.exists(path):
#             return []

#         with open(path, "r", encoding="utf-8") as f:

#             return json.load(f)

#     # =====================================================
#     # SAFE STRING
#     # =====================================================

#     @staticmethod
#     def safe_lower(value):

#         if value is None:
#             return ""

#         return str(value).lower()

#     # =====================================================
#     # PRODUCT MATCH
#     # =====================================================
#     @staticmethod
#     def find_product_metadata(
#         products,
#         hs_code
#     ):

#         result = {
#             "country": None,
#             "certification": None,
#             "manufacturer": None,
#             "product_name": None,
#             "model": None,
#             "technical_regulation": None,
#             "hs_code": hs_code
#         }

#         for item in products:

#             # ======================================
#             # MATCH HS CODE
#             # ======================================

#             if item.get("hs_code") != hs_code:
#                 continue

#             clauses = item.get("clause", [])

#             for clause in clauses:

#                 clause_type = (
#                     clause.get("type", "")
#                     .strip()
#                     .lower()
#                 )

#                 value = clause.get("value")

#                 # ======================================
#                 # COUNTRY
#                 # ======================================

#                 if clause_type == "country of origin":

#                     result["country"] = value

#                 # ======================================
#                 # CERTIFICATION
#                 # ======================================

#                 elif clause_type == "certification":

#                     result["certification"] = value

#                 # ======================================
#                 # MANUFACTURER
#                 # ======================================

#                 elif clause_type == "manufacturer":

#                     result["manufacturer"] = value

#                 # ======================================
#                 # PRODUCT NAME
#                 # ======================================

#                 elif clause_type == "product name":

#                     result["product_name"] = value

#                 # ======================================
#                 # MODEL
#                 # ======================================

#                 elif clause_type == "model":

#                     result["model"] = value

#                 # ======================================
#                 # TECHNICAL REGULATION
#                 # ======================================

#                 elif clause_type == "technical regulation":

#                     result["technical_regulation"] = value

#             return result

    
#     @staticmethod
#     def normalize_text(text):

#         if text is None:
#             return ""

#         text = str(text).lower()

#         # remove special chars
#         text = text.replace("-", " ")
#         text = text.replace("_", " ")

#         # remove extra spaces
#         text = " ".join(text.split())

#         return text

#     @staticmethod
#     def match_product(product_name, item):

#         text = QueryService.normalize_text(
#             json.dumps(item)
#         )

#         product_words = QueryService.normalize_text(
#             product_name
#         ).split()

#         matched_words = 0

#         for word in product_words:

#             if word in text:

#                 matched_words += 1

#         # ------------------------------------------------
#         # MATCH SCORE
#         # ------------------------------------------------

#         score = matched_words / len(product_words)

#         return score >= 0.7

#     # =====================================================
#     # MAIN ENGINE
#     # =====================================================

#     @staticmethod
#     def process_query(query: str):

#         # =================================================
#         # STEP 1: UNDERSTAND QUERY
#         # =================================================

#         entities = extract_query_entities(query)
#         extended_entities = extract_query_entities_extended(query)
        
#         print(f"Extracted entities: {entities}")
#         print(f"Extracted extended entities: {extended_entities}")
#         # if entities
#         hs_code = extended_entities.get("hs_code")
#         # print(f"Extracted HS code: {hs_code}")
#         intent = extended_entities.get("intent")
#         print("intent", intent)


#         product_name = entities.get("product_name")
#         # print(f"Extracted product name: {product_name}")

#         market = entities.get("market", "KSA")

#         # =================================================
#         # STEP 2: EMPTY RESPONSE TEMPLATE
#         # =================================================

#         compliance_result = {

#             "query": query,

#             "product": {},

#             "standards": [],

#             "technical_regulations": [],

#             "certificates": [],

#             "risk_assessment": [],

#             "saber_requirements": [],

#             "compliance_status": "NOT_FOUND"
#         }

#         # =================================================
#         # STEP 3: NO PRODUCT FOUND
#         # =================================================

#         if not product_name and not hs_code:

#             compliance_result["message"] = "No product identified"

#             return compliance_result

#         # =================================================
#         # STEP 4: LOAD DATA
#         # =================================================

#         products = QueryService.load_json("items.json")

#         standards = QueryService.load_json("std_results.json")

#         technical_regulations = QueryService.load_json("tr_results.json")

#         saber_rules = QueryService.load_json("saber_results.json")

#         ksa_rules = QueryService.load_json("ksa_saleem.json")

#         # =================================================
#         # STEP 5: FIND PRODUCT
#         # =================================================

#         matched_product = None
#         # print(f"Looking for product match in database with name: {product_name} and HS code: {hs_code}")
#         if  hs_code:
#             print(f"Trying to match product using HS code: {hs_code}")
#             for item in products:
#                 if item.get("hs_code") == str(hs_code):
#                     # print(f"Extracted product name from HS code: {item.get('product_name')}")
                 
         
#                     matched_product = item
#                     break

                    
                   
         
#         if product_name:
#             for item in products:
#                 if QueryService.match_product(product_name, item["product_name"]):
                  
#                     matched_product = item
#                     break
#             # hs_code = matched_product.get("hs_code")
#             print(f"Extracted HS code from matched product: {hs_code}")

#         if matched_product is None:

#             compliance_result["message"] = "No matching product found in database"

#             return compliance_result
#         product_name = matched_product.get("product_name", product_name)
#         hs_code = matched_product.get("hs_code", hs_code)
#         TR_NAME = matched_product.get("clause", {})
#         for item in TR_NAME:
#              if item.get("type", "").lower() == "Regulation".lower():
#                 TR_NAME = item.get("value")
#                 break
#         print(f"Extracted TR_NAME from matched product: {TR_NAME}")
#         if matched_product:

#             compliance_result["product"] = matched_product
#         # print(f"Matched product: {matched_product}")
        

#         # =================================================
#         # STEP 6: FIND STANDARDS
#         # =================================================

#         matched_standards = []

#         for item in standards:

#             if QueryService.match_product(product_name, item):

#                 matched_standards.append(item)

#         # print(f"Matched standards: {matched_standards}")

#         compliance_result["standards"] = matched_standards

#         # =================================================
#         # STEP 7: FIND TECHNICAL REGULATIONS
#         # =================================================

#         matched_tr = []
        

#         for item in technical_regulations:
#             if hs_code:
#                 if QueryService.match_product(hs_code[:4], item["metaText"]):
     
#                     item["metaText"] = TextCleaner.normalize_text(item["metaText"])
#                     item["hs_code"] = hs_code
#                     TR_NAME = item["title"]
#                     matched_tr.append(item)
#                     break
#             if hs_code and not matched_tr:
#                 if QueryService.match_product(TR_NAME, item["file_name"]):
#                     TR_NAME = item["title"]
#                     matched_tr.append(item)
#                     break

        

#         # print(f"Matched technical regulations: {matched_tr}")   
#         compliance_result["technical_regulations"] = matched_tr
#         matched_product['TR_NAME'] = TR_NAME

#         # =================================================
#         # STEP 8: FIND SABER REQUIREMENTS
#         # =================================================

#         matched_saber = []

#         for item in saber_rules:

#             if QueryService.match_product(product_name, item):

#                 matched_saber.append(item)
#         # print(f"Matched saber requirements: {matched_saber}")

#         compliance_result["saber_requirements"] = matched_saber

#         # =================================================
#         # STEP 9: FIND KSA SALEEM RULES
#         # =================================================

#         matched_ksa = []

#         for item in ksa_rules:

#             if QueryService.match_product(product_name, item):

#                 matched_ksa.append(item)

#         # ADD INTO TECHNICAL REGULATIONS
        

#         compliance_result["technical_regulations"].extend(matched_ksa)

#         # =================================================
#         # STEP 10: EXTRACT CERTIFICATES
#         # =================================================

#         certificates = []

#         for item in matched_product.get("clause", []):

#             clause_type = QueryService.safe_lower(
#                 item.get("type")
#             )

#             if "certificate" in clause_type:

#                 certificates.append(item)
#         # print(f"Extracted certificates: {certificates}")

#         compliance_result["certificates"] = certificates

#         # =================================================
#         # STEP 11: RISK ASSESSMENT
#         # =================================================

#         risks = []

#         for item in matched_product.get("clause", []):

#             clause_type = QueryService.safe_lower(
#                 item.get("type")
#             )

#             if "risk" in clause_type:

#                 risks.append(item)
#         # print(f"Extracted risks: {risks}")

#         compliance_result["risk_assessment"] = risks

#         # =================================================
#         # STEP 12: COMPLIANCE DECISION
#         # =================================================

#         missing = []

#         if not matched_standards:
#             missing.append("standards")

#         if not matched_tr:
#             for item in technical_regulations:
#                 if QueryService.match_product(TR_NAME, item):
#                     matched_tr.append(item)
#             if not matched_tr:
#                 missing.append("technical regulations")

#         if not matched_saber:
#             missing.append("saber requirements")

#         # -------------------------------------------------

#         if len(missing) == 0:

#             compliance_result["compliance_status"] = "PASS"

#         else:

#             compliance_result["compliance_status"] = "PARTIAL"

#             compliance_result["missing"] = missing

  
#         # if intent is None:
            
#         #     resultsss = build_compliance_response(compliance_result)
#         #     return resultsss
#         # print("rreee",resultsss)
#         return handle_query(intent,compliance_result)


# =========================================================
# FILE: app/services/query_service.py
# =========================================================

from numpy import ma

from app.utils.HsCodeRegex import HSCodeService
from app.utils.intent_result_builder import handle_query
from app.utils.responseBuilder import ComplianceResponseBuilder
from app.utils.response_formatter import ResponseFormatter

import json
import os

from app.utils.query_parser import (
    extract_query_entities,
    extract_query_entities_extended
)

from app.utils.text_cleaner import TextCleaner


class QueryService:

    # =====================================================
    # LOAD JSON
    # =====================================================

    @staticmethod
    async def load_json(path):

        if not os.path.exists(path):
            return []

        with open(path, "r", encoding="utf-8") as f:

            return json.load(f)

    # =====================================================
    # SAFE STRING
    # =====================================================

    @staticmethod
    async def safe_lower(value):

        if value is None:
            return ""

        return str(value).lower()

    # =====================================================
    # NORMALIZE TEXT
    # =====================================================

    @staticmethod
    async def normalize_text(text):

        if text is None:
            return ""

        text = str(text).lower()

        text = text.replace("-", " ")
        text = text.replace("_", " ")

        text = " ".join(text.split())

        return text

    # =====================================================
    # MATCH PRODUCT
    # =====================================================

    @staticmethod
    async def match_product(product_name, item):

        text = await QueryService.normalize_text(
            json.dumps(item)
        )

        product_words = (
            await QueryService.normalize_text(
                product_name
            )
        ).split()

        matched_words = 0

        for word in product_words:

            if word in text:
                matched_words += 1

        score = matched_words / len(product_words)

        return score >= 0.7

    # =====================================================
    # FIND PRODUCT METADATA
    # =====================================================

    @staticmethod
    async def find_product_metadata(
        products,
        hs_code
    ):

        result = {
            "country": None,
            "certification": None,
            "manufacturer": None,
            "product_name": None,
            "model": None,
            "technical_regulation": None,
            "hs_code": hs_code
        }

        for item in products:

            if item.get("hs_code") != hs_code:
                continue

            clauses = item.get("clause", [])

            for clause in clauses:

                clause_type = (
                    clause.get("type", "")
                    .strip()
                    .lower()
                )

                value = clause.get("value")

                if clause_type == "country of origin":

                    result["country"] = value

                elif clause_type == "certification":

                    result["certification"] = value

                elif clause_type == "manufacturer":

                    result["manufacturer"] = value

                elif clause_type == "product name":

                    result["product_name"] = value

                elif clause_type == "model":

                    result["model"] = value

                elif clause_type == "technical regulation":

                    result["technical_regulation"] = value

            return result

    # =====================================================
    # MAIN ENGINE
    # =====================================================

    @staticmethod
    async def process_query(query: str):

        # =================================================
        # STEP 1: UNDERSTAND QUERY
        # =================================================

        entities = extract_query_entities(query)

        extended_entities = (
            extract_query_entities_extended(query)
        )

        print(f"Extracted entities: {entities}")

        print(
            f"Extracted extended entities: "
            f"{extended_entities}"
        )

        hs_code = extended_entities.get("hs_code")

        intent = extended_entities.get("intent")

        print("intent", intent)

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

        if not product_name and not hs_code:

            compliance_result[
                "message"
            ] = "No product identified"

            return compliance_result

        # =================================================
        # STEP 4: LOAD DATA
        # =================================================

        products = await QueryService.load_json(
            "items.json"
        )

        standards = await QueryService.load_json(
            "std_results.json"
        )

        technical_regulations = (
            await QueryService.load_json(
                "tr_results.json"
            )
        )

        saber_rules = await QueryService.load_json(
            "saber_results.json"
        )

        ksa_rules = await QueryService.load_json(
            "ksa_saleem.json"
        )

        # =================================================
        # STEP 5: FIND PRODUCT
        # =================================================

        matched_product = None

        if hs_code:

            print(
                f"Trying to match product "
                f"using HS code: {hs_code}"
            )

            for item in products:

                if item.get("hs_code") == str(hs_code):

                    matched_product = item
                    break

        if product_name:
            print("yess i debug it now")

            for item in products:

                matched = (
                    await QueryService.match_product(
                        product_name,
                        item["product_name"]
                    )
                )

                if matched:

                    matched_product = item
                    break

        if matched_product is None:

            compliance_result[
                "message"
            ] = (
                "No matching product "
                "found in database"
            )

            return compliance_result

        product_name = matched_product.get(
            "product_name",
            product_name
        )

        hs_code = matched_product.get(
            "hs_code",
            hs_code
        )

        TR_NAME = matched_product.get(
            "clause",
            {}
        )

        for item in TR_NAME:

            if (
                item.get("type", "").lower()
                == "regulation"
            ):

                TR_NAME = item.get("value")
                break

        matched_product["TR_NAME"] = TR_NAME

        compliance_result[
            "product"
        ] = matched_product

        # =================================================
        # STEP 6: FIND STANDARDS
        # =================================================

        matched_standards = []

        for item in standards:

            matched = (
                await QueryService.match_product(
                    product_name,
                    item
                )
            )

            if matched:
                matched_standards.append(item)

        compliance_result[
            "standards"
        ] = matched_standards

        # =================================================
        # STEP 7: FIND TECHNICAL REGULATIONS
        # =================================================

        matched_tr = []

        for item in technical_regulations:

            if hs_code:

                matched = (
                    await QueryService.match_product(
                        hs_code[:4],
                        item["metaText"]
                    )
                )

                if matched:

                    item["metaText"] = (
                        TextCleaner.normalize_text(
                            item["metaText"]
                        )
                    )

                    item["hs_code"] = hs_code

                    TR_NAME = item["title"]

                    matched_tr.append(item)

                    break

        compliance_result[
            "technical_regulations"
        ] = matched_tr

        # =================================================
        # STEP 8: FIND SABER REQUIREMENTS
        # =================================================

        matched_saber = []

        for item in saber_rules:

            matched = (
                await QueryService.match_product(
                    product_name,
                    item
                )
            )

            if matched:
                matched_saber.append(item)

        compliance_result[
            "saber_requirements"
        ] = matched_saber

        # =================================================
        # STEP 9: FIND KSA SALEEM RULES
        # =================================================

        matched_ksa = []

        for item in ksa_rules:

            matched = (
                await QueryService.match_product(
                    product_name,
                    item
                )
            )

            if matched:
                matched_ksa.append(item)

        compliance_result[
            "technical_regulations"
        ].extend(matched_ksa)

        # =================================================
        # STEP 10: CERTIFICATES
        # =================================================

        certificates = []

        for item in matched_product.get(
            "clause",
            []
        ):

            clause_type = (
                await QueryService.safe_lower(
                    item.get("type")
                )
            )

            if "certificate" in clause_type:

                certificates.append(item)

        compliance_result[
            "certificates"
        ] = certificates

        # =================================================
        # STEP 11: RISK
        # =================================================

        risks = []

        for item in matched_product.get(
            "clause",
            []
        ):

            clause_type = (
                await QueryService.safe_lower(
                    item.get("type")
                )
            )

            if "risk" in clause_type:

                risks.append(item)

        compliance_result[
            "risk_assessment"
        ] = risks

        # =================================================
        # STEP 12: STATUS
        # =================================================

        missing = []

        if not matched_standards:
            missing.append("standards")

        if not matched_tr:
            missing.append(
                "technical regulations"
            )

        if not matched_saber:
            missing.append(
                "saber requirements"
            )

        if len(missing) == 0:

            compliance_result[
                "compliance_status"
            ] = "PASS"

        else:

            compliance_result[
                "compliance_status"
            ] = "PARTIAL"

            compliance_result[
                "missing"
            ] = missing

        # =================================================
        # STEP 13: HANDLE INTENT
        # =================================================

        return await handle_query(
            intent,
            compliance_result
        )