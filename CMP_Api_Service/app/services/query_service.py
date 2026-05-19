# =========================================================
# FILE: app/services/query_service.py
# =========================================================

from numpy import ma
from app.utils.intent_result_builder import handle_query
import json
import os

from app.utils.query_parser import extract_query_entities, extract_query_entities_extended
from app.utils.text_cleaner import TextCleaner
# =================
# Knowledge db
# ==================
from app.services.standard_service import StandardService
from app.services.ksa_saleem_service import KSASaleemService
from app.services.hs_code_service  import HSCodeService
from app.services.product_item_servce import ProductService
from app.services.saber_service  import SaberService
from app.services.technical_regulation_service import TechnicalRegulationService
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.saber_workflow import build_compliance_response
class QueryService:
    def __init__(self, db: AsyncSession):

        self.db = db

        self.product_service = ProductService(db)

        self.standard_service = StandardService(db)

        self.tr_service = (
            TechnicalRegulationService(db)
        )

        self.saber_service = SaberService(db)

        self.ksa_service = KSASaleemService(db)
        self.hs_code_service = HSCodeService(db)

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

    async def process_query(self,query: str):

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

       # =================================================
# STEP 4: LOAD DATA FROM DATABASE
# =================================================

        products = await self.product_service.get_all()

        standards = await (
            self.standard_service.get_all()
        )

        technical_regulations = await (
            self.tr_service.get_all()
        )

        saber_rules = await (
            self.saber_service.get_all()
        )

        ksa_rules = await (
            self.ksa_service.get_all()
        )

        hs_codes = await (
            self.hs_code_service.get_all()
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
                    print("item_id", item["id"])

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
                    print("item_id", item["id"])
                    

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
        print("product name",product_name)

        for item in standards:

            matched = (
                await QueryService.match_product(
                    product_name,
                    item
                )
            )

            if matched:
                print("std_name",item["std_name"])
                print("file_name",item["file_name"])
                print("std_id", item["id"])
                
                
                matched_standards.append(item)
                break

        compliance_result[
            "standards"
        ] = matched_standards
        # print("stdddd", matched_standards)  

        # =================================================
        # STEP 7: FIND TECHNICAL REGULATIONS
        # =================================================

        matched_tr = []

        for item in technical_regulations:

            if hs_code:

                matched = (
                    await QueryService.match_product(
                        hs_code[:4],
                        item["text"]
                    )
                )

                if matched:
                    print("std_id", item["id"])
                    

                    item["metaText"] = (
                        TextCleaner.normalize_text(
                            item["text"]
                        )
                    )

                    item["hs_code"] = hs_code

                    TR_NAME = item["tr_name"]

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
                print("saber_id", item["id"])
                
                matched_saber.append(item)
                break

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
                print("ksa_id", item["id"])
                
                matched_ksa.append(item)
                break

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
        return build_compliance_response(compliance_result["product"])
       

        return await handle_query(
            intent,
            compliance_result
        )