import re


class pcocFIleClause:

    # =====================================================
    # CLEAN TEXT
    # =====================================================

    @staticmethod
    def normalize_text(text):

        if not text:
            return ""

        # remove extra spaces
        text = re.sub(
            r'\s+',
            ' ',
            text
        )

        # fix merged words
        text = re.sub(
            r'(\d)([A-Z])',
            r'\1 \2',
            text
        )

        text = re.sub(
            r'([a-z])([A-Z])',
            r'\1 \2',
            text
        )

        return text.strip()

    # =====================================================
    # GENERIC EXTRACTOR
    # =====================================================

    @staticmethod
    def extract_value(
        text,
        patterns,
        default=None,
        clean=True
    ):

        if isinstance(patterns, str):

            patterns = [patterns]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:

                value = (
                    match.group(1)
                    .strip()
                )

                # =========================================
                # CLEAN VALUE
                # =========================================

                if clean:

                    value = re.sub(
                        r'\s+',
                        ' ',
                        value
                    )

                    value = re.sub(
                        r'[/\\]{2,}',
                        ' ',
                        value
                    )

                    value = value.strip(
                        " -:/.,()"
                    )

                return value

        return default

    # =====================================================
    # MAIN METHOD
    # =====================================================

    @staticmethod
    def extractClause(text):

        if not text:
            return {}

        # =================================================
        # NORMALIZE
        # =================================================

        text = (
            pcocFIleClause
            .normalize_text(text)
        )

        # =================================================
        # RESULT
        # =================================================

        result = {

            # =============================================
            # CERTIFICATE NUMBER
            # =============================================

            "certificate_number":

                pcocFIleClause.extract_value(

                    text,

                    [
                        r'certificate\s*number\s*([A-Z0-9\-]+)'
                    ]
                ),

            # =============================================
            # ISSUE DATE
            # =============================================

            "issue_date":

                pcocFIleClause.extract_value(

                    text,

                    [
                        r'issue\s*date\s*(\d{2}/\d{2}/\d{4})'
                    ]
                ),

            # =============================================
            # EXPIRY DATE
            # =============================================

            "expiry_date":

                pcocFIleClause.extract_value(

                    text,

                    [
                        r'expire\s*date\s*(\d{2}/\d{2}/\d{4})'
                    ]
                ),

            # =============================================
            # CERTIFICATE TYPE
            # =============================================

            "certificate_type":

                "COC"

                if re.search(
                    r'certificate\s*\(coc\)',
                    text,
                    re.IGNORECASE
                )

                else None,

            # =============================================
            # COMMERCIAL REGISTRATION
            # =============================================

            "commercial_registration":

                pcocFIleClause.extract_value(

                    text,

                    [
                        r'commercial\s*registration\s*no\s*([0-9\s\/\-]+)'
                    ]
                ),

            # =============================================
            # ESTABLISHMENT ADDRESS
            # =============================================

            "establishment_address":

                pcocFIleClause.extract_value(

                    text,

                    [
                        r'establishment\s*address\s*(.*?)\s*product\s*and\s*manufacturer\s*data'
                    ]
                ),

            # =============================================
            # MODEL
            # =============================================

            "model":

                pcocFIleClause.extract_value(

                    text,

                    [
                        r'model\s*type\s*([A-Z0-9\-_]+)',

                        r'model\s*name\s*([A-Z0-9\-_]+)',

                        r'model\s*number\s*([A-Z0-9\-_]+)'
                    ]
                ),

            # =============================================
            # BRAND
            # =============================================

            "brand":

                pcocFIleClause.extract_value(

                    text,

                    [
                        r'trade\s*mark\s*([a-zA-Z0-9\s\-_&]+?)\s*product\s*name'
                    ]
                ),

            # =============================================
            # PRODUCT NAME
            # =============================================

            "product_name":

                pcocFIleClause.extract_value(

                    text,

                    [

                        r'product\s*name\s*(.*?)\s*\(/\)',

                        r'product\s*name\s*(.*?)\s*product\s*description'
                    ]
                ),

            # =============================================
            # PRODUCT DESCRIPTION
            # =============================================

            "product_description":

                pcocFIleClause.extract_value(

                    text,

                    [
                        r'product\s*description\s*(.*?)\s*country\s*of\s*origin'
                    ]
                ),

            # =============================================
            # COUNTRY OF ORIGIN
            # =============================================

            "country_of_origin":

                pcocFIleClause.extract_value(

                    text,

                    [
                        r'country\s*of\s*origin\s*(.*?)\s*hs\s*code'
                    ]
                ),

            # =============================================
            # HS CODE
            # =============================================

            "hs_code":

                pcocFIleClause.extract_value(

                    text,

                    [
                        r'hs\s*code\s*(\d{4,12})'
                    ]
                ),

            # =============================================
            # TECHNICAL REGULATION
            # =============================================

            "technical_regulation":

                pcocFIleClause.extract_value(

                    text,

                    [
                        r'technical\s*regulation\s*(technical\s*regulation\s*for\s*.*?)\s*manufacturer\s*name'
                    ]
                ),

            # =============================================
            # MANUFACTURER
            # =============================================

            "manufacturer":

                pcocFIleClause.extract_value(

                    text,

                    [
                        r'manufacturer\s*name\s*(.*?)\s*manufacturer\s*address'
                    ]
                ),

            # =============================================
            # MANUFACTURER ADDRESS
            # =============================================

            "manufacturer_address":

                pcocFIleClause.extract_value(

                    text,

                    [
                        r'manufacturer\s*address\s*(.*?)\s*product\s*test\s*data'
                    ]
                ),

            # =============================================
            # COMPLIANCE DECISION
            # =============================================

            "compliance_decision":

                pcocFIleClause.extract_value(

                    text,

                    [
                        r'decision\s*of\s*confomity\s*assessment\s*(.*?)\s*cb\s*organization'
                    ]
                )
        }

        # =================================================
        # REMOVE EMPTY VALUES
        # =================================================

        cleaned_result = {

            key: value

            for key, value in result.items()

            if value not in [None, ""]
        }

        return cleaned_result