
def certification_query(data):
    """
    Generate certification response
    """

    product = data.get("product", {})
    pcoc = product.get("pcocData", {})

    # -----------------------------------
    # Product Name
    # -----------------------------------
    product_name = (
        pcoc.get("product_name")
        or product.get("product_name")
        or "Unknown Product"
    )

    # -----------------------------------
    # Required Certifications
    # -----------------------------------
    required_certifications = []

    # Product Certificate
    if pcoc:
        required_certifications.append("PCoC")

    # Shipment Certificate
    if product.get("TR_NAME"):
        required_certifications.append("SCoC")

    # Remove duplicate values
    required_certifications = list(
        dict.fromkeys(required_certifications)
    )

    # -----------------------------------
    # Issuing Authority
    # -----------------------------------
    issuing_authority = "SASO"

    # -----------------------------------
    # Summary
    # -----------------------------------
    summary = (
        f"{product_name} require SABER conformity "
        f"certification before sale in Saudi Arabia."
    )

    # -----------------------------------
    # Final Response
    # -----------------------------------
    response = {
        "intent": "certification_query",

        "product_name": product_name,

        "required_certifications": required_certifications,

        "issuing_authority": issuing_authority,

        "summary": summary
    }

    return response