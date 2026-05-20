import re


def extract_standards(text):
    """
    Generic standards extraction
    """

    standards = re.findall(
        r'(ISO(?:\/TS)?\s*\d+|IEC\s*\d+|ASTM\s*\w+)',
        text,
        flags=re.I
    )

    return list(set(standards))


def extract_documents(text):
    """
    Generic document extraction
    """

    document_keywords = [
        "MSDS",
        "technical file",
        "certificate",
        "declaration of conformity",
        "risk assessment",
        "test report",
        "manual",
        "quality management system"
    ]

    found = []

    lower_text = text.lower()

    for doc in document_keywords:

        if doc.lower() in lower_text:
            found.append(doc)

    return list(set(found))


def detect_requirement_type(text):
    """
    Generic requirement classifier
    """

    lower_text = text.lower()

    if "msds" in lower_text:
        return "document_requirement"

    if "technical file" in lower_text:
        return "conformity_requirement"

    if "quality management" in lower_text:
        return "quality_management_requirement"

    if "logo" in lower_text:
        return "product_marking_requirement"

    if "standard" in lower_text:
        return "technical_standard_requirement"

    if "traffic regulations" in lower_text:
        return "administrative_requirement"

    if "international system of units" in lower_text:
        return "metrological_requirement"

    return "general_requirement"


def is_mandatory(text):
    """
    Detect mandatory clauses
    """

    mandatory_keywords = [
        "shall",
        "must",
        "required",
        "mandatory"
    ]

    lower_text = text.lower()

    return any(
        word in lower_text
        for word in mandatory_keywords
    )


def transform_regulation_structure(
    req_data,
    article_no="4",
    article_title="Obligations of Supplier"
):
    """
    Convert parsed regulation tree
    into structured compliance clauses
    """

    response = {
        "article": {
            "article_no": article_no,
            "title": article_title
        },
        "clauses": []
    }

    # ---------------------------------------------------
    # LOOP MAIN CLAUSES
    # ---------------------------------------------------

    for clause_id, clause_data in req_data.items():

        title = clause_data.get("title", "")

        intro = clause_data.get("intro", "")

        items = clause_data.get("items", {})

        clause_obj = {
            "clause_id": clause_id,
            "title": title,
            "intro": intro,
            "mandatory": is_mandatory(
                intro or title
            )
        }

        # ---------------------------------------------------
        # HAS SUB CLAUSES
        # ---------------------------------------------------

        if items:

            sub_clauses = []

            for item_id, item_text in items.items():

                # -----------------------------------------
                # ORIGINAL REF
                #
                # 4/1/11 -> 4/111
                # -----------------------------------------

                parts = item_id.split("/")

                original_ref = (
                    f"{parts[0]}/{parts[1]}{parts[2]}"
                )

                sub_clause = {
                    "clause_id": item_id,

                    "original_ref": original_ref,

                    "type": detect_requirement_type(
                        item_text
                    ),

                    "requirement": item_text,

                    "mandatory": is_mandatory(
                        item_text
                    )
                }

                # -----------------------------------------
                # STANDARDS
                # -----------------------------------------

                standards = extract_standards(
                    item_text
                )

                if standards:
                    sub_clause["standards"] = standards

                # -----------------------------------------
                # DOCUMENTS
                # -----------------------------------------

                documents = extract_documents(
                    item_text
                )

                if documents:
                    sub_clause[
                        "required_documents"
                    ] = documents

                sub_clauses.append(sub_clause)

            clause_obj["sub_clauses"] = sub_clauses

        # ---------------------------------------------------
        # DIRECT REQUIREMENT
        # ---------------------------------------------------

        else:

            clause_obj["requirement"] = intro

            clause_obj["type"] = (
                detect_requirement_type(
                    intro
                )
            )

            standards = extract_standards(
                intro
            )

            if standards:
                clause_obj[
                    "standards"
                ] = standards

            documents = extract_documents(
                intro
            )

            if documents:
                clause_obj[
                    "required_documents"
                ] = documents

        response["clauses"].append(
            clause_obj
        )

    return response