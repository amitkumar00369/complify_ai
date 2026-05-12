from .intententResponse.detailsResponse import build_compliance_response
from .intententResponse.product_search import product_search
def handle_query(intent_result,data):

    primary_intent = intent_result["primary_intent"]
    print("innnntess",primary_intent)

    if primary_intent == "market_access":

        return product_search(
            data
        )

    elif primary_intent == "export_eligibility":

        return handle_export_eligibility(
            intent_result
        )

    elif primary_intent == "document_requirement":

        return handle_document_requirement(
            intent_result
        )

    elif primary_intent == "standard_lookup":

        return handle_standard_lookup(
            intent_result
        )

    elif primary_intent == "technical_regulation_lookup":

        return handle_tr_lookup(
            intent_result
        )

    elif primary_intent == "saber_requirement":

        return handle_saber_requirement(
            intent_result
        )

    elif primary_intent == "certificate_lookup":

        return handle_certificate_lookup(
            intent_result
        )

    elif primary_intent == "hs_code_lookup":

        return handle_hs_code_lookup(
            intent_result
        )

    else:

        return build_compliance_response(
            data
        )