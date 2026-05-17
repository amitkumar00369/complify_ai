import re
def parse_clause(text):
    clause = {
        "field": None,
        "rule_type": None,
        "action": {},
        "market": "KSA",
        "mandatory": False
    }

    text_lower = text.lower()

    # FIELD
    if "voltage" in text_lower:
        clause["field"] = "voltage"
    elif "frequency" in text_lower:
        clause["field"] = "frequency"
    elif "test report" in text_lower:
        clause["field"] = "test_report"

    # RULE TYPE
    if "between" in text_lower:
        clause["rule_type"] = "range"
    elif "required" in text_lower:
        clause["rule_type"] = "required"
    elif "must be" in text_lower:
        clause["rule_type"] = "exact"

    # NUMBERS
    nums = re.findall(r'\d+', text)
    if len(nums) >= 2:
        clause["action"]["min"] = int(nums[0])
        clause["action"]["max"] = int(nums[1])
    elif len(nums) == 1:
        clause["action"]["value"] = int(nums[0])

    # UNIT
    if "v" in text_lower:
        clause["action"]["unit"] = "V"
    elif "hz" in text_lower:
        clause["action"]["unit"] = "Hz"

    # MANDATORY
    if "must" in text_lower or "required" in text_lower:
        clause["mandatory"] = True

    return clause