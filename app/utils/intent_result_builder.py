
from .intententResponse.compliance_response import ComplianceService
INTENT_METHOD_MAP = {
    "market_access": ComplianceService.product_search,

    "export_eligibility": (
        ComplianceService.export_eligibility
    ),

    "document_requirement": (
        ComplianceService.document_requirement
    ),

    "standard_lookup": (
        ComplianceService.standard_query
    ),

    "technical_regulation_lookup": (
        ComplianceService.technical_regulation_query
    ),

    "saber_requirement": (
        ComplianceService.saber_query
    ),

    "certificate_lookup": (
        ComplianceService.certification_query
    ),

    "hs_code_lookup": (
        ComplianceService.hs_code_query
    ),

    "iec_standard_lookup": (
        ComplianceService.iec_standard_query
    )
}


async def handle_query(intent_result, data):

    try:

        primary_intent = (
            intent_result.get("primary_intent")
        )

        print("PRIMARY INTENT =>", primary_intent)

        method = INTENT_METHOD_MAP.get(
            primary_intent,
            ComplianceService.build_compliance_response
        )

        response = await method(data)

        return response

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }