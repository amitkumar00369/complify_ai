def detect_standard(text):
    t = text.lower()

    if any(k in t for k in ["voltage", "frequency"]):
        return "IEC 60335"

    if any(k in t for k in ["test report", "certificate"]):
        return "SABER"

    return "UNKNOWN"