from ..services.regulation_parser_service import RegulationParserService

def extract_hs_mapping(text: str):
    """
    Extract standards + HS codes properly (single call)
    """

    
    # print("Extracting HS mapping from text (length:", len(text), ")")

    if not text or len(text) < 50:
        return {}

    result = RegulationParserService.process_regulation(text)
    

    return result