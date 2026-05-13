

def saber_query(data):
    """
    Generate SABER compliance response
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
    # Detect SABER Requirement
    # -----------------------------------
    saber_required = True

    # -----------------------------------
    # Requirements
    # -----------------------------------
    requirements = [
        "PCoC",
        "Arabic Label",
        "Technical Datasheet",
        "Importer Registration"
    ]

    # Add dynamic requirements
    if product.get("standard_name"):
        requirements.append("Technical Report")

    if product.get("TR_NAME"):
        requirements.append("SCoC")

    # Chemical related products
    chemical_keywords = [
        "spray",
        "chemical",
        "cleaner",
        "paint",
        "detergent",
        "liquid"
    ]

    product_name_lower = product_name.lower()

    if any(
        keyword in product_name_lower
        for keyword in chemical_keywords
    ):
        requirements.append("MSDS")

    # Remove duplicate values
    requirements = list(
        dict.fromkeys(requirements)
    )

    # -----------------------------------
    # Summary
    # -----------------------------------
    summary = (
        f"{product_name} requires SABER registration "
        f"before import into Saudi Arabia."
    )

    # -----------------------------------
    # Final Response
    # -----------------------------------
    response = {
        "intent": "saber_query",

        "product_name": product_name,

        "saber_required": saber_required,

        "requirements": requirements,

        "summary": summary
    }

    return response