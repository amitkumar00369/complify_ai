
def standard_query(data):
    try:
        product_name = data.get("product_name")
        standards = data.get("standards", [])
        summary = data.get("summary", "")

        formatted_standards = []

        for standard in standards:
            formatted_standards.append({
                "standard_number": standard.get("standard_number"),
                "title": standard.get("title")
            })

        response = {
            "success": True,
            "intent": data.get("intent"),
            "product_name": product_name,
            "standards": formatted_standards,
            "summary": summary,
            "message": f"Standards fetched successfully for {product_name}"
        }

        return response

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }