

def document_requirement(data):
    """
    Generate document requirement response
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
    # Required Documents
    # -----------------------------------
    required_documents = [
        "Technical Report",
        "Arabic Label",
        "Risk Assessment",
        "SDoC",
        "Invoice",
        "Product Images"
    ]

    # -----------------------------------
    # Optional Dynamic Documents
    # -----------------------------------
    if product.get("standard_name"):
        required_documents.append("Test Report")

    if pcoc.get("certificate_number"):
        required_documents.append("Existing Certificate Copy")

    # Remove duplicate values
    required_documents = list(
        dict.fromkeys(required_documents)
    )

    # -----------------------------------
    # Compliance Status
    # -----------------------------------
    compliance_status = "Documents Required"

    # -----------------------------------
    # Summary
    # -----------------------------------
    summary = (
        "The listed compliance documents are "
        "required before product approval "
        "in Saudi Arabia."
    )

    # -----------------------------------
    # Final Response
    # -----------------------------------
    response = {
        "intent": "document_requirement",

        "product_name": product_name,

        "required_documents": required_documents,

        "compliance_status": compliance_status,

        "summary": summary
    }

    return response