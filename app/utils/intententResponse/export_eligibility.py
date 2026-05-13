
def export_eligibility(data):
    """
    Generate export eligibility response
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
    # Detect Chemical Related Product
    # -----------------------------------
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

    product_name_lower = product_name.lower()

    chemical_review_required = any(
        keyword in product_name_lower
        for keyword in chemical_keywords
    )

    # -----------------------------------
    # Compliance Status
    # -----------------------------------
    if chemical_review_required:
        compliance_status = "Conditional Approval"
    else:
        compliance_status = "Eligible"

    # -----------------------------------
    # Required Documents
    # -----------------------------------
    required_documents = [
        "MSDS",
        "Arabic Label",
        "Invoice",
        "Product Specification"
    ]

    # -----------------------------------
    # Recommendations
    # -----------------------------------
    recommendations = []

    if chemical_review_required:
        recommendations.extend([
            "Verify chemical restrictions",
            "Check SASO/GSO chemical regulations"
        ])
    else:
        recommendations.append(
            "Proceed with SABER registration"
        )

    # -----------------------------------
    # Summary
    # -----------------------------------
    if chemical_review_required:
        summary = (
            "The product may require additional "
            "chemical compliance validation before "
            "export to Saudi Arabia."
        )
    else:
        summary = (
            "The product appears eligible for export "
            "to Saudi Arabia subject to standard "
            "SABER compliance requirements."
        )

    # -----------------------------------
    # Final Response
    # -----------------------------------
    response = {
        "intent": "export_eligibility",

        "product_name": product_name,

        "compliance_status": compliance_status,

        "data": {
            "regulated": True,
            "chemical_review_required": chemical_review_required,

            "required_documents": required_documents
        },

        "recommendations": recommendations,

        "summary": summary
    }

    return response