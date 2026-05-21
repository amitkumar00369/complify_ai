import re
from typing import Dict, List, Any
from collections import OrderedDict


# ============================================================
# MAIN ENTRY
# ============================================================

def extract_ksa_compliance_data(
    raw_text: str
) -> Dict[str, Any]:

    text = preprocess_ocr_text(raw_text)

    clause_blocks = extract_clause_blocks(
        text
    )

    result = {
        "metadata": extract_metadata(text),
        "products": extract_products(text),
        "technologies": extract_technologies(text),
        "frequency_bands": extract_frequency_bands(text),
        "voice_services": extract_voice_services(text),
        "requirements": [],
        "recommendations": [],
        "labeling": [],
        "obligations": [],
        "limits": extract_limits(text),
        "alerts": extract_alerts(text),
        "references": extract_references(text),
        "clauses": [],
        "clause_objects": [],
        "tables": [],
        "clause_hierarchy": [],
    }

    # ========================================================
    # CLAUSE PARSING
    # ========================================================

    for clause_id, clause_text in clause_blocks.items():

        cleaned_text = normalize_sentence(
            clean_text(clause_text)
        )

        cleaned_text = remove_suffix_noise(
            cleaned_text
        )

        if not cleaned_text.strip():
            continue

        clause_title = get_clause_title(
            clause_id
        )

        clause_type = detect_clause_type(
            cleaned_text
        )

        technologies = find_technologies(
            cleaned_text
        )

        bands = find_bands(
            cleaned_text
        )

        parent_clause = get_parent_clause(
            clause_id
        )

        clause_obj = {
            "clause_id": clause_id,
            "title": clause_title,
            "type": clause_type,
            "text": cleaned_text,
            "technologies": technologies,
            "bands": bands,
            "parent_clause": parent_clause,
        }

        # ====================================================
        # AVOID DUPLICATE CLAUSE OBJECTS
        # ====================================================

        existing_ids = {
            x["clause_id"]
            for x in result["clause_objects"]
        }

        if clause_id not in existing_ids:

            result["clause_objects"].append(
                clause_obj
            )

        result["clauses"].append(
            clause_id
        )

        # ====================================================
        # REQUIREMENTS
        # ====================================================

        if clause_type == "mandatory_requirement":

            result["requirements"].append({
                "clause": clause_id,
                "severity": "mandatory",
                "text": cleaned_text,
                "technologies": technologies,
                "bands": bands,
            })

        # ====================================================
        # RECOMMENDATIONS
        # ====================================================

        if clause_type == "recommended_requirement":

            result["recommendations"].append({
                "clause": clause_id,
                "severity": "recommended",
                "text": cleaned_text,
            })

        # ====================================================
        # LABELING
        # ====================================================

        if "e-label" in cleaned_text.lower():

            result["labeling"].append({
                "clause": clause_id,
                "type": "e-label",
                "text": cleaned_text,
            })

        # ====================================================
        # OBLIGATIONS
        # ====================================================

        if (
            "responsibility of the manufacturer"
            in cleaned_text.lower()
            or "operators shall"
            in cleaned_text.lower()
        ):

            result["obligations"].append({
                "clause": clause_id,
                "text": cleaned_text,
            })

    # ========================================================
    # TABLES
    # ========================================================

    result["tables"] = extract_alert_tables(
        text
    )

    # ========================================================
    # CLAUSE HIERARCHY
    # ========================================================

    result["clause_hierarchy"] = (
        build_clause_hierarchy(
            result["clauses"]
        )
    )

    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    for key in [
        "requirements",
        "recommendations",
        "labeling",
        "obligations",
        "tables",
    ]:

        result[key] = deduplicate(
            result[key]
        )

    result["clauses"] = sorted(
        list(set(result["clauses"]))
    )

    return result


# ============================================================
# OCR CLEANER
# ============================================================

def preprocess_ocr_text(text: str) -> str:

    text = text.lower()

    # fix merged clause starts
    text = re.sub(
        r"([a-z])(\d-\d)",
        r"\1 \2",
        text
    )

    # spacing after colon
    text = re.sub(
        r"([a-z])(:)([a-z0-9])",
        r"\1: \3",
        text
    )

    OCR_FIXES = {

        # voice services
        r"vo\s+lte":
            "volte",

        r"vo\s+wifi":
            "vowifi",

        # wireless
        r"5g\s+nr":
            "5gnr",

        r"wifi\s+6e":
            "wifi6e",

        r"wifi\s+6":
            "wifi6",

        # spacing after technologies
        r"lte:":
            "lte: ",

        r"5gnr:":
            "5gnr: ",

        r"nb-iot/lte-m:":
            "nb-iot/lte-m: ",

        # OCR mistakes
        r"wifi 6note":
            "wifi 6 note",

        r"n78note":
            "n78 note",

        # merged words
        r"cstalso":
            "cst also",

        r"devicesper":
            "devices per",

        r"supportingthe":
            "supporting the",

        r"supportofthe":
            "support of the",

        r"thesupport":
            "the support",

        r"cstfor":
            "cst for",

        r"technologie lte":
            "technology lte",

        r"operatingsystem":
            "operating system",

        r"thebrand":
            "the brand",

        # mandatory wording
        r"mustsupport":
            "must support",

        r"shallsupport":
            "shall support",

        r"requiredto":
            "required to",

        r"mustbe":
            "must be",

        r"shallbe":
            "shall be",

        # spacing fixes
        r"all handsetsmust":
            "all handsets must",

        r"cste-label":
            "cst e-label",

        r"communicationsservices":
            "communications services",

        # security alerts
        r"alerts\s+\(category\s+4\)\s+security alerts":
            "security alerts (category 4)",

        # clause fixes
        r"3-\s*2-\s*2\s*-\s*1":
            "3-2-2-1",

        r"3-\s*2-\s*2\s*-\s*2":
            "3-2-2-2",

        r"3-\s*2-\s*2\s*-\s*3":
            "3-2-2-3",
    }

    for pattern, replacement in OCR_FIXES.items():

        text = re.sub(
            pattern,
            replacement,
            text,
            flags=re.I
        )

    # normalize spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# CLAUSE EXTRACTION
# ============================================================

def extract_clause_blocks(text):

    CLAUSE_REGEX = re.compile(
        r"""
        (?<!\.)
        \b
        (?:[1-9]|[1-9]\d)
        (?:-(?:[1-9]|[1-9]\d)){1,3}
        \b
        (?!\.\d)
        """,
        re.X
    )

    matches = list(
        CLAUSE_REGEX.finditer(text)
    )

    clauses = OrderedDict()

    for i, match in enumerate(matches):

        clause_id = match.group()

        if not is_valid_clause(
            clause_id
        ):
            continue

        start = match.end()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(text)

        clause_text = text[start:end]

        clause_text = stop_at_headers(
            clause_text
        )

        clause_text = clean_text(
            clause_text
        )

        if len(clause_text) > 8:

            clauses[clause_id] = (
                clause_text
            )

    return clauses


# ============================================================
# STOP HEADERS
# ============================================================

def stop_at_headers(text):

    STOP_HEADERS = [
        "appendix",
        "table",
        "requirements for",
    ]

    for stop in STOP_HEADERS:

        idx = text.lower().find(stop)

        if idx >= 0:

            text = text[:idx]

            break

    return text


# ============================================================
# CLAUSE TITLES
# ============================================================

SECTION_TITLES = {
    "3-2": "Technology Requirements",
    "3-3": "Frequency Requirements",
    "3-4": "Voice Services Requirements",
    "3-5": "Emergency Communication Requirements",
    "3-6": "E-Label Requirements",
    "4-2": "Router Technology Requirements",
    "4-3": "Router Frequency Requirements",
    "5-2": "IoT Technology Requirements",
    "5-3": "IoT Frequency Requirements",
}


def get_clause_title(clause):

    for prefix, title in SECTION_TITLES.items():

        if (
            clause == prefix
            or clause.startswith(
                prefix + "-"
            )
        ):

            return title

    return "General Clause"


# ============================================================
# CLAUSE TYPE DETECTOR
# ============================================================

def detect_clause_type(text):

    text = text.lower()

    if any(
        k in text
        for k in [
            "must",
            "shall",
            "required to",
            "mandatory",
        ]
    ):

        return (
            "mandatory_requirement"
        )

    if any(
        k in text
        for k in [
            "strongly encourages",
            "recommended",
            "should support",
            "should include",
        ]
    ):

        return (
            "recommended_requirement"
        )

    return "general"


# ============================================================
# METADATA
# ============================================================

def extract_metadata(text):

    metadata = {}

    year = re.search(
        r"\b(20\d{2})\b",
        text
    )

    if year:
        metadata["year"] = (
            year.group(1)
        )

    doc = re.search(
        r"document number:\s*([a-zA-Z0-9\-]+)",
        text,
        re.I
    )

    if doc:
        metadata[
            "document_number"
        ] = doc.group(1).upper()

    revision = re.search(
        r"revision:\s*([^\.]{1,30})",
        text,
        re.I
    )

    if revision:
        metadata["revision"] = (
            revision.group(1).strip()
        )

    title = re.search(
        r"technical specification requirements for ([^.]{5,60})",
        text,
        re.I
    )

    if title:
        metadata["title"] = (
            "Technical Specification Requirements for "
            + title.group(1).strip()
        )

    return metadata


# ============================================================
# PRODUCTS
# ============================================================

def extract_products(text):

    products = []

    patterns = [
        "mobile phones",
        "tablets",
        "mobile computers",
        "mobile routers",
        "customer premises equipment",
        "cellular iot devices",
    ]

    for p in patterns:

        if p in text:

            products.append(
                p.title()
            )

    return sorted(
        list(set(products))
    )


# ============================================================
# TECHNOLOGIES
# ============================================================

TECH_ALIASES = {
    "lte": "LTE",
    "4g": "4G",
    "5gnr": "5G NR",
    "nb-iot": "NB-IoT",
    "lte-m": "LTE-M",
    "wifi6": "WiFi 6",
    "wifi6e": "WiFi 6E",
    "esim": "eSIM",
    "volte": "VoLTE",
    "vowifi": "VoWiFi",
    "vonr": "VoNR",
    "vinr": "ViNR",
    "cbs": "CBS",
    "aml": "AML",
}


def extract_technologies(text):

    technologies = []

    for key, value in (
        TECH_ALIASES.items()
    ):

        if key in text.lower():

            technologies.append(
                value
            )

    return sorted(
        list(set(technologies))
    )


def find_technologies(text):

    found = []

    for key, value in (
        TECH_ALIASES.items()
    ):

        if key in text.lower():

            found.append(
                value
            )

    return sorted(
        list(set(found))
    )


# ============================================================
# FREQUENCY BANDS
# ============================================================

def extract_frequency_bands(text):

    bands = re.findall(
        r"\b([bn]\d+)\b",
        text,
        re.I
    )

    lte = []
    nr = []

    for band in bands:

        if band.lower().startswith("b"):

            lte.append(
                band.upper()
            )

        elif band.lower().startswith("n"):

            nr.append(
                band.upper()
            )

    result = []

    if lte:

        result.append({
            "technology": "LTE",
            "bands": sorted(
                list(set(lte))
            )
        })

    if nr:

        result.append({
            "technology": "5G NR",
            "bands": sorted(
                list(set(nr))
            )
        })

    return result


def find_bands(text):

    return sorted(
        list(
            set(
                re.findall(
                    r"\b([bn]\d+)\b",
                    text,
                    re.I
                )
            )
        )
    )


# ============================================================
# VOICE SERVICES
# ============================================================

def extract_voice_services(text):

    services = []

    patterns = {
        r"volte": "VoLTE",
        r"vowifi": "VoWiFi",
        r"vonr": "VoNR",
        r"vinr": "ViNR",
    }

    for pattern, label in (
        patterns.items()
    ):

        if re.search(
            pattern,
            text,
            re.I
        ):

            services.append(
                label
            )

    return sorted(
        list(set(services))
    )


# ============================================================
# LIMITS
# ============================================================

def extract_limits(text):

    limits = []

    matches = re.finditer(
        r"(\d+(?:\.\d+)?)\s*(seconds|mhz|ghz)",
        text,
        re.I
    )

    for m in matches:

        limits.append({
            "value":
                m.group(1),

            "unit":
                m.group(2).lower()
        })

    return deduplicate(limits)


# ============================================================
# ALERTS
# ============================================================

def extract_alerts(text):

    alerts = re.findall(
        r"category\s+\d+",
        text,
        re.I
    )

    return sorted(
        list(set(alerts))
    )


# ============================================================
# REFERENCES
# ============================================================

def extract_references(text):

    refs = []

    patterns = [
        "cst",
        "saso",
        "cma",
        "iot regulatory framework",
    ]

    for p in patterns:

        if p.lower() in text.lower():

            refs.append(
                p.upper()
            )

    return refs


# ============================================================
# TABLE EXTRACTION
# ============================================================

def extract_alert_tables(text):

    tables = []

    pattern = re.compile(
        r"(\d{4})\s+"
        r"(\d{4})\s+"
        r"([a-z\s]+?)\s*"
        r"\(category\s*(\d+)\)",
        re.I
    )

    for match in pattern.finditer(text):

        tables.append({

            "primary_channel":
                match.group(1),

            "secondary_channel":
                match.group(2),

            "alert_name":
                clean_text(
                    match.group(3)
                ),

            "category":
                match.group(4),
        })

    return deduplicate(tables)


# ============================================================
# CLAUSE HIERARCHY
# ============================================================

def build_clause_hierarchy(
    clauses
):

    hierarchy = []

    clauses = sorted(
        list(set(clauses))
    )

    for clause in clauses:

        parent = (
            get_parent_clause(
                clause
            )
        )

        hierarchy.append({
            "clause": clause,
            "parent": parent,
        })

    return hierarchy


def get_parent_clause(clause):

    parts = clause.split("-")

    if len(parts) <= 2:
        return None

    return "-".join(
        parts[:-1]
    )


# ============================================================
# NOISE CLEANER
# ============================================================

def remove_suffix_noise(text):

    REMOVE_SUFFIXES = [
        "technology requirements:",
        "frequency requirements:",
        "voice services requirements:",
        "emergency communications services requirements:",
        "e-label requirements:",
        "general requirements:",
    ]

    for suffix in REMOVE_SUFFIXES:

        if text.endswith(suffix):

            text = text.replace(
                suffix,
                ""
            ).strip()

    return text


# ============================================================
# VALIDATORS
# ============================================================

def is_valid_clause(clause):

    return bool(
        re.match(
            r"^\d+-\d+(?:-\d+)*$",
            clause
        )
    )


# ============================================================
# HELPERS
# ============================================================

def clean_text(text):

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    # remove trailing broken clauses
    text = re.sub(
        r"\.\d-\s*$",
        ".",
        text
    )

    text = re.sub(
        r"\b\d-\s*$",
        "",
        text
    )

    return text.strip()


def normalize_sentence(text):

    fixes = {

        "all handsetsmust":
            "all handsets must",

        "devicesper":
            "devices per",

        "supportofthe":
            "support of the",

        "cstalso":
            "cst also",

        "wifi6":
            "wifi 6",

        "wifi6e":
            "wifi 6e",

        "b40and":
            "b40 and",

        "accessibleby":
            "accessible by",

        "cstfor":
            "cst for",

        "technologie lte":
            "technology lte",

        "operatingsystem":
            "operating system",

        "thebrand":
            "the brand",
    }

    for old, new in fixes.items():

        text = text.replace(
            old,
            new
        )

    return text


def deduplicate(items):

    seen = set()

    result = []

    for item in items:

        key = str(item)

        if key not in seen:

            seen.add(key)

            result.append(item)

    return result