
def technical_regulation_query(data):
    try:
        product_name = data.get("product_name")
        technical_regulations = data.get("technical_regulations", [])
        summary = data.get("summary", "")

        formatted_regulations = []

        for regulation in technical_regulations:
            formatted_regulations.append({
                "name": regulation.get("name"),
                "authority": regulation.get("authority")
            })

        response = {
            "success": True,
            "intent": data.get("intent"),
            "product_name": product_name,
            "technical_regulations": formatted_regulations,
            "summary": summary,
            "message": f"Technical regulations fetched successfully for {product_name}"
        }

        return response

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }