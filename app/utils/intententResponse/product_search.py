# {
#   "intent": "product_search",
#   "query": "I want to sell electric cooking range in KSA",
#   "product_name": "Commercial Cooking Range",
#   "hs_code": "841981000002",
#   "compliance_status": "Regulated Product",
#   "data": {
#     "technical_regulations": [
#       "Technical Regulation for Machinery Safety"
#     ],
#     "required_certifications": [
#       "PCoC",
#       "SCoC"
#     ],
#     "standards": [
#       "IEC 60335-2-36"
#     ]
#   },
#   "recommendations": [
#     "Register product on SABER platform",
#     "Prepare technical documents",
#     "Verify Arabic labeling"
#   ],
#   "next_steps": [
#     "Apply for Product Certificate",
#     "Upload Technical Report"
#   ],
#   "summary": "The electric cooking range can be sold in Saudi Arabia after fulfilling SABER compliance requirements."
# }


import re


def extract_standard_codes(text):
    """
    Extract IEC/ISO standard codes from text
    """

    if not text:
        return []

    pattern = r'(IEC\s*\d+(?:-\d+)*)'
    matches = re.findall(pattern, text, re.IGNORECASE)

    return list(dict.fromkeys([
        m.upper().replace("  ", " ")
        for m in matches
    ]))


def product_search(data):
    """
    Generate normalized compliance response
    for product search intent
    """

    product = data.get("product", {})
    pcoc = product.get("pcocData", {})

    # -----------------------------------
    # Product Details
    # -----------------------------------
    product_name = (
        pcoc.get("product_name")
        or product.get("product_name")
    )

    hs_code = (
        pcoc.get("hs_code")
        or product.get("hs_code")
    )

    # -----------------------------------
    # Standards
    # -----------------------------------
    standards_text = (
        product.get("standard_name")
        or product.get("product_info")
        or ""
    )

    standards = extract_standard_codes(standards_text)

    # -----------------------------------
    # Technical Regulations
    # -----------------------------------
    technical_regulations = []

    if pcoc.get("technical_regulation"):
        technical_regulations.append(
            pcoc.get("technical_regulation")
        )

    # -----------------------------------
    # Required Certifications
    # -----------------------------------
    required_certifications = []

    if pcoc:
        required_certifications.append("PCoC")

    if product.get("TR_NAME"):
        required_certifications.append("SCoC")

    # -----------------------------------
    # Compliance Status
    # -----------------------------------
    compliance_status = "Regulated Product"

    # -----------------------------------
    # Recommendations
    # -----------------------------------
    recommendations = [
        "Register product on SABER platform",
        "Prepare technical documents",
        "Verify Arabic labeling"
    ]

    # -----------------------------------
    # Next Steps
    # -----------------------------------
    next_steps = [
        "Apply for Product Certificate",
        "Upload Technical Report"
    ]

    # -----------------------------------
    # Summary
    # -----------------------------------
    summary = (
        f"The {product_name.lower()} can be sold "
        f"in Saudi Arabia after fulfilling "
        f"SABER compliance requirements."
    )

    # -----------------------------------
    # Final Response
    # -----------------------------------
    response = {
        "intent": "product_search",
        # "query": data.get("query"),

        "product_name": product_name,

        "hs_code": hs_code,

        "compliance_status": compliance_status,

        "data": {
            "technical_regulations": technical_regulations,

            "required_certifications": required_certifications,

            "standards": standards
        },

        "recommendations": recommendations,

        "next_steps": next_steps,

        "summary": summary
    }

    return response