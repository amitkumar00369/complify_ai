import re


def extract_standard_codes(standard_text):
    """
    Extract IEC/ISO standard codes from text.
    Example:
    'IEC 60335-2-36; IEC 60335-1'
    ->
    ['IEC 60335-2-36', 'IEC 60335-1']
    """

    if not standard_text:
        return []

    pattern = r'(IEC\s*\d+(?:-\d+)*(?:-\d+)?)'
    matches = re.findall(pattern, standard_text, re.IGNORECASE)

    return list(dict.fromkeys([m.upper().replace("  ", " ") for m in matches]))


def build_compliance_response(all_data):
    """
    Build normalized compliance response
    """

    product = all_data.get("product", {})
    pcoc = product.get("pcocData", {})

    # -----------------------------
    # Standards
    # -----------------------------
    standards_raw = (
        product.get("standard_name")
        or product.get("product_info")
        or ""
    )

    standards = extract_standard_codes(standards_raw)

    # -----------------------------
    # Compliance Status
    # -----------------------------
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

    # -----------------------------
    # Required Certificates
    # -----------------------------
    required_certificates = []

    if pcoc:
        required_certificates.append("PCoC")

    tr_name = product.get("TR_NAME")

    if tr_name:
        required_certificates.append("SCoC")

    # -----------------------------
    # Required Documents
    # -----------------------------
    required_documents = [
        "Technical Report",
        "Arabic Label",
        "Invoice",
        "Risk Assessment"
    ]

    # -----------------------------
    # Final Response
    # -----------------------------
    response = {
        "product_name": pcoc.get("product_name"),
        "model": (
            product.get("modelName", [None])[0]
            if product.get("modelName")
            else None
        ),
        "brand": pcoc.get("brand"),
        "manufacturer": pcoc.get("manufacturer"),
        "manufacturer_address": pcoc.get("manufacturer_address"),
        "country_of_origin": pcoc.get("country_of_origin"),
        "hs_code": pcoc.get("hs_code"),
        "technical_regulation": pcoc.get("technical_regulation"),

        "standards": standards,

        "required_certificates": required_certificates,
        "required_documents": required_documents,

        "certificate_number": pcoc.get("certificate_number"),
        "issue_date": pcoc.get("issue_date"),
        "expiry_date": pcoc.get("expiry_date"),

        "market": "Saudi Arabia",
        "authority": "SASO",

        "compliance_status": compliance_status,

        "confidence": product.get("confidence"),
        "valid": product.get("valid")
    }

    return response