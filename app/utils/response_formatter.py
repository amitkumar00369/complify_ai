class ResponseFormatter:

    @staticmethod
    def format_response(data):

        formatted = {

            "query": data.get("query"),

            "product": {
                "product_name": data["product"].get("product_name"),
                "hs_code": data["product"].get("hs_code"),
                "standard": data["product"].get("standard_name")
            },

            "required_standards": [],

            "technical_regulations": [],

            "required_certificates": [],

            "important_requirements": [],

            "compliance_status": data.get("compliance_status")
        }

        # -----------------------------------
        # STANDARDS
        # -----------------------------------

        for std in data.get("standards", []):

            std_name = (
                std.get("clause", {})
                .get("metadata", {})
                .get("standard_code")
            )

            if std_name:
                formatted["required_standards"].append(std_name)

        # -----------------------------------
        # CERTIFICATES
        # -----------------------------------

        for cert in data.get("certificates", []):

            value = cert.get("value")

            if value:
                formatted["required_certificates"].append(value)

        # -----------------------------------
        # REQUIREMENTS
        # -----------------------------------

        for std in data.get("standards", []):

            requirements = (
                std.get("clause", {})
                .get("requirements", [])
            )

            for req in requirements[:5]:

                formatted["important_requirements"].append(
                    req.get("requirement")
                )

        return formatted