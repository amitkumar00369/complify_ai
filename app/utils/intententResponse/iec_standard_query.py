
def iec_standard_query(data):
    try:
        product_name = data.get("product_name")
        iec_standards = data.get("iec_standards", [])
        summary = data.get("summary", "")

        response = {
            "success": True,
            "intent": data.get("intent"),
            "product_name": product_name,
            "iec_standards": iec_standards,
            "summary": summary,
            "message": f"IEC standards fetched successfully for {product_name}"
        }

        return response

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }