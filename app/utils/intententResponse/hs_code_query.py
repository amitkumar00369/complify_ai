
import re


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


def hs_code_query(data):
    """
    Generate HS Code compliance response
    """

    product = data.get("product", {})
    pcoc = product.get("pcocData", {})

    # -----------------------------------
    # HS Code
    # -----------------------------------
    hs_code = (
        pcoc.get("hs_code")
        or product.get("hs_code")
    )

    # -----------------------------------
    # Product Category
    # -----------------------------------
    product_category = (
        pcoc.get("product_name")
        or product.get("product_name")
        or "Unknown Product"
    )

    # -----------------------------------
    # Technical Regulations
    # -----------------------------------
    technical_regulations = []

    technical_regulation = pcoc.get(
        "technical_regulation"
    )

    if technical_regulation:

        # Short clean regulation name
        if "machinery" in technical_regulation.lower():
            technical_regulations.append(
                "Machinery Safety TR"
            )
        else:
            technical_regulations.append(
                technical_regulation
            )

    # -----------------------------------
    # Required Certifications
    # -----------------------------------
    required_certifications = []

    if pcoc:
        required_certifications.append("PCoC")

    if product.get("TR_NAME"):
        required_certifications.append("SCoC")

    required_certifications = list(
        dict.fromkeys(required_certifications)
    )

    # -----------------------------------
    # Standards
    # -----------------------------------
    standards_text = (
        product.get("standard_name")
        or product.get("product_info")
        or ""
    )

    standards = extract_standard_codes(
        standards_text
    )

    # -----------------------------------
    # Summary
    # -----------------------------------
    summary = (
        "This HS code belongs to regulated "
        "commercial cooking equipment."
    )

    # -----------------------------------
    # Final Response
    # -----------------------------------
    response = {
        "intent": "hs_code_query",

        "hs_code": hs_code,

        "product_category": product_category,

        "technical_regulations": technical_regulations,

        "required_certifications": required_certifications,

        "standards": standards,

        "summary": summary
    }

    return response