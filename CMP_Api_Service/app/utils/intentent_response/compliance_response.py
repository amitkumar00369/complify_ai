import re


class ComplianceService:

    @staticmethod
    def extract_standard_codes(text):
        """
        Extract IEC/ISO standard codes
        """

        if not text:
            return []

        pattern = r'(IEC\s*\d+(?:-\d+)*)'

        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE
        )

        return list(dict.fromkeys([
            m.upper().replace("  ", " ")
            for m in matches
        ]))

    # ---------------------------------------------------
    # Certification Query
    # ---------------------------------------------------

    @staticmethod
    async def certification_query(data):

        try:

            product = data.get("product", {})
            pcoc = product.get("pcoc_data", {})

            product_name = (
                pcoc.get("product_name")
                or product.get("product_name")
                or "Unknown Product"
            )

            required_certifications = []

            if pcoc:
                required_certifications.append("PCoC")

            if product.get("TR_NAME"):
                required_certifications.append("SCoC")

            required_certifications = list(
                dict.fromkeys(required_certifications)
            )

            response = {
                "success": True,
                "intent": "certification_query",
                "product_name": product_name,
                "required_certifications": required_certifications,
                "issuing_authority": "SASO",
                "summary": (
                    f"{product_name} require SABER conformity "
                    f"certification before sale in Saudi Arabia."
                )
            }

            return response

        except Exception as e:

            return {
                "success": False,
                "message": str(e)
            }

    # ---------------------------------------------------
    # Document Requirement
    # ---------------------------------------------------

    @staticmethod
    async def document_requirement(data):

        try:

            product = data.get("product", {})
            pcoc = product.get("pcoc_data", {})

            product_name = (
                pcoc.get("product_name")
                or product.get("product_name")
                or "Unknown Product"
            )

            required_documents = [
                "Technical Report",
                "Arabic Label",
                "Risk Assessment",
                "SDoC",
                "Invoice",
                "Product Images"
            ]

            if product.get("standard_name"):
                required_documents.append("Test Report")

            if pcoc.get("certificate_number"):
                required_documents.append(
                    "Existing Certificate Copy"
                )

            required_documents = list(
                dict.fromkeys(required_documents)
            )

            response = {
                "success": True,
                "intent": "document_requirement",
                "product_name": product_name,
                "required_documents": required_documents,
                "compliance_status": "Documents Required",
                "summary": (
                    "The listed compliance documents are "
                    "required before product approval "
                    "in Saudi Arabia."
                )
            }

            return response

        except Exception as e:

            return {
                "success": False,
                "message": str(e)
            }

    # ---------------------------------------------------
    # Export Eligibility
    # ---------------------------------------------------

    @staticmethod
    async def export_eligibility(data):

        try:

            product = data.get("product", {})
            pcoc = product.get("pcoc_data", {})

            product_name = (
                pcoc.get("product_name")
                or product.get("product_name")
                or "Unknown Product"
            )

            chemical_keywords = [
                "spray",
                "cleaner",
                "chemical",
                "paint",
                "detergent",
                "liquid",
                "solvent",
                "disinfectant"
            ]

            chemical_review_required = any(
                keyword in product_name.lower()
                for keyword in chemical_keywords
            )

            compliance_status = (
                "Conditional Approval"
                if chemical_review_required
                else "Eligible"
            )

            response = {
                "success": True,
                "intent": "export_eligibility",
                "product_name": product_name,
                "compliance_status": compliance_status,
                "data": {
                    "regulated": True,
                    "chemical_review_required": (
                        chemical_review_required
                    ),
                    "required_documents": [
                        "MSDS",
                        "Arabic Label",
                        "Invoice",
                        "Product Specification"
                    ]
                },
                "summary": (
                    "The product appears eligible for export "
                    "to Saudi Arabia."
                )
            }

            return response

        except Exception as e:

            return {
                "success": False,
                "message": str(e)
            }

    # ---------------------------------------------------
    # HS Code Query
    # ---------------------------------------------------

    @staticmethod
    async def hs_code_query(data):

        try:

            product = data.get("product", {})
            pcoc = product.get("pcoc_data", {})

            standards_text = (
                product.get("standard_name")
                or product.get("product_info")
                or ""
            )

            standards = (
                ComplianceService.extract_standard_codes(
                    standards_text
                )
            )

            response = {
                "success": True,
                "intent": "hs_code_query",
                "hs_code": (
                    pcoc.get("hs_code")
                    or product.get("hs_code")
                ),
                "product_category": (
                    pcoc.get("product_name")
                    or product.get("product_name")
                ),
                "technical_regulations": [
                    pcoc.get("technical_regulation")
                ] if pcoc.get("technical_regulation") else [],
                "required_certifications": [
                    "PCoC"
                ],
                "standards": standards,
                "summary": (
                    "This HS code belongs to regulated "
                    "commercial equipment."
                )
            }

            return response

        except Exception as e:

            return {
                "success": False,
                "message": str(e)
            }

    # ---------------------------------------------------
    # IEC Standard Query
    # ---------------------------------------------------

    @staticmethod
    async def iec_standard_query(data):

        try:

            response = {
                "success": True,
                "intent": data.get("intent"),
                "product_name": data.get("product_name"),
                "iec_standards": data.get(
                    "iec_standards",
                    []
                ),
                "summary": data.get("summary"),
                "message": (
                    "IEC standards fetched successfully"
                )
            }

            return response

        except Exception as e:

            return {
                "success": False,
                "message": str(e)
            }

    # ---------------------------------------------------
    # Product Search
    # ---------------------------------------------------

    @staticmethod
    async def product_search(data):

        try:

            product = data.get("product", {})
            pcoc = product.get("pcoc_data", {})

            standards_text = (
                product.get("standard_name")
                or product.get("product_info")
                or ""
            )

            standards = (
                ComplianceService.extract_standard_codes(
                    standards_text
                )
            )

            response = {
                "success": True,
                "intent": "product_search",
                "product_name": (
                    pcoc.get("product_name")
                    or product.get("product_name")
                ),
                "hs_code": (
                    pcoc.get("hs_code")
                    or product.get("hs_code")
                ),
                "compliance_status": "Regulated Product",
                "data": {
                    "technical_regulations": [
                        pcoc.get("technical_regulation")
                    ] if pcoc.get(
                        "technical_regulation"
                    ) else [],
                    "required_certifications": [
                        "PCoC"
                    ],
                    "standards": standards
                },
                "summary": (
                    "Product requires SABER compliance."
                )
            }

            return response

        except Exception as e:

            return {
                "success": False,
                "message": str(e)
            }

    # ---------------------------------------------------
    # Saber Query
    # ---------------------------------------------------

    @staticmethod
    async def saber_query(data):

        try:

            product = data.get("product", {})
            pcoc = product.get("pcoc_data", {})

            product_name = (
                pcoc.get("product_name")
                or product.get("product_name")
                or "Unknown Product"
            )

            requirements = [
                "PCoC",
                "Arabic Label",
                "Technical Datasheet",
                "Importer Registration"
            ]

            if product.get("standard_name"):
                requirements.append("Technical Report")

            if product.get("TR_NAME"):
                requirements.append("SCoC")

            response = {
                "success": True,
                "intent": "saber_query",
                "product_name": product_name,
                "saber_required": True,
                "requirements": list(
                    dict.fromkeys(requirements)
                ),
                "summary": (
                    f"{product_name} requires SABER "
                    f"registration before import "
                    f"into Saudi Arabia."
                )
            }

            return response

        except Exception as e:

            return {
                "success": False,
                "message": str(e)
            }

    # ---------------------------------------------------
    # Standard Query
    # ---------------------------------------------------

    @staticmethod
    async def standard_query(data):

        try:

            formatted_standards = []

            for standard in data.get("standards", []):

                formatted_standards.append({
                    "standard_number": (
                        standard.get("standard_number")
                    ),
                    "title": standard.get("title")
                })

            response = {
                "success": True,
                "intent": data.get("intent"),
                "product_name": data.get("product_name"),
                "standards": formatted_standards,
                "summary": data.get("summary"),
                "message": (
                    "Standards fetched successfully"
                )
            }

            return response

        except Exception as e:

            return {
                "success": False,
                "message": str(e)
            }

    # ---------------------------------------------------
    # Technical Regulation Query
    # ---------------------------------------------------

    @staticmethod
    async def technical_regulation_query(data):

        try:

            formatted_regulations = []

            for regulation in data.get(
                "technical_regulations",
                []
            ):

                formatted_regulations.append({
                    "name": regulation.get("name"),
                    "authority": regulation.get(
                        "authority"
                    )
                })

            response = {
                "success": True,
                "intent": data.get("intent"),
                "product_name": data.get("product_name"),
                "technical_regulations": (
                    formatted_regulations
                ),
                "summary": data.get("summary"),
                "message": (
                    "Technical regulations fetched "
                    "successfully"
                )
            }

            return response

        except Exception as e:

            return {
                "success": False,
                "message": str(e)
            }
        # ---------------------------------------------------
    # Default Compliance Response
    # ---------------------------------------------------

    @staticmethod
    async def build_compliance_response(data):

        try:

            product = data.get("product", {})
            pcoc = product.get("pcoc_data", {})

            standards_raw = (
                product.get("standard_name")
                or product.get("product_info")
                or ""
            )

            standards = (
                ComplianceService.extract_standard_codes(
                    standards_raw
                )
            )

            decision = (
                pcoc.get("compliance_decision")
                or ""
            )

            if "approved" in decision.lower():

                compliance_status = "Approved"

            elif "reject" in decision.lower():

                compliance_status = "Rejected"

            else:

                compliance_status = "Pending"

            required_certificates = []

            if pcoc:
                required_certificates.append("PCoC")

            if product.get("TR_NAME"):
                required_certificates.append("SCoC")

            response = {
                "success": True,

                "intent": "build_compliance_response",

                "product_name": (
                    pcoc.get("product_name")
                ),

                "model": (
                    product.get("modelName", [None])[0]
                    if product.get("modelName")
                    else None
                ),

                "brand": pcoc.get("brand"),

                "manufacturer": (
                    pcoc.get("manufacturer")
                ),

                "manufacturer_address": (
                    pcoc.get(
                        "manufacturer_address"
                    )
                ),

                "country_of_origin": (
                    pcoc.get("country_of_origin")
                ),

                "hs_code": pcoc.get("hs_code"),

                "technical_regulation": (
                    pcoc.get(
                        "technical_regulation"
                    )
                ),

                "standards": standards,

                "required_certificates": (
                    required_certificates
                ),

                "required_documents": [
                    "Technical Report",
                    "Arabic Label",
                    "Invoice",
                    "Risk Assessment"
                ],

                "certificate_number": (
                    pcoc.get(
                        "certificate_number"
                    )
                ),

                "issue_date": (
                    pcoc.get("issue_date")
                ),

                "expiry_date": (
                    pcoc.get("expiry_date")
                ),

                "market": "Saudi Arabia",

                "authority": "SASO",

                "compliance_status": (
                    compliance_status
                ),

                "confidence": (
                    product.get("confidence")
                ),

                "valid": product.get("valid")
            }

            return response

        except Exception as e:

            return {
                "success": False,
                "message": str(e)
            }