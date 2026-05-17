def validate_clause(clause):
    print(" validating clause:", clause)
    errors = []

    if not clause.get("field"):
        errors.append("Missing field")

    if not clause.get("rule_type"):
        errors.append("Missing rule_type")

    if clause.get("rule_type") == "range":
        if "min" not in clause["action"] or "max" not in clause["action"]:
            errors.append("Invalid range values")

    if clause.get("rule_type") == "exact":
        if "value" not in clause["action"]:
            errors.append("Missing exact value")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }