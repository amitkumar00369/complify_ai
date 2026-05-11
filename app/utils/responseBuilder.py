class ComplianceResponseBuilder:

    # ==========================================
    # MAIN RESPONSE
    # ==========================================

    @staticmethod
    def build_response(
        query,
        matched_product,
        matched_trs,
        matched_standards
    ):

        return {

            "query": query,

            "product":
                ComplianceResponseBuilder.build_product(
                    matched_product
                ),

            "technical_regulations":
                ComplianceResponseBuilder.build_trs(
                    matched_trs
                ),

            "standards":
                ComplianceResponseBuilder.build_standards(
                    matched_standards
                )
        }

    # ==========================================
    # PRODUCT
    # ==========================================

    @staticmethod
    def build_product(product):

        if not product:
            return {}

        return {

            "product_name":
                product.get(
                    "product_name"
                ),

            "model":
                product.get(
                    "modelName"
                ),

            "hs_code":
                product.get(
                    "hs_code"
                ),

            "standard_name":
                product.get(
                    "standard_name"
                ),

            "country":
                product.get(
                    "country"
                ),

            "manufacturer":
                product.get(
                    "manufacturer"
                ),

            "certificate_type":
                product.get(
                    "certificateName"
                ),

            "technical_regulation":
                product.get(
                    "TR_NAME"
                )
        }

    # ==========================================
    # TECHNICAL REGULATIONS
    # ==========================================

    @staticmethod
    def build_trs(
        matched_trs
    ):

        trs = []

        for tr in matched_trs:

            trs.append({

                "tr_name":
                    tr.get(
                        "title"
                    ),

                "matched_hs_code":
                    tr.get(
                        "hs_code"
                    ),

                "matched_text":
                    tr.get(
                        "descriptions"
                    )

              
            })

        return trs

    # ==========================================
    # STANDARDS
    # ==========================================

    @staticmethod
    def build_standards(
        matched_standards
    ):

        standards = []

        for std in matched_standards:

            clause = std.get(
                "clause",
                {}
            )

            metadata = clause.get(
                "metadata",
                {}
            )

            standards.append({

                "standard":
                    metadata.get(
                        "standard_code"
                    ),

                "year":
                    metadata.get(
                        "year"
                    ),

                "title":
                    metadata.get(
                        "title"
                    ),

                "requirements_count":
                    len(
                        clause.get(
                            "requirements",
                            []
                        )
                    ),

                "clauses_count":
                    len(
                        clause.get(
                            "clauses",
                            []
                        )
                    )
            })
            break

        return standards