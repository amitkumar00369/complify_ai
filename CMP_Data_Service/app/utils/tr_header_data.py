# import re
# from typing import Dict


# def extract_tr_cover_metadata(raw_text: str) -> Dict:
#     """
#     Generic SASO TR metadata extractor.
#     Missing fields are returned as 'N/A'
#     """

#     # ---------------------------------------------------------
#     # CLEAN TEXT
#     # ---------------------------------------------------------
#     text = raw_text

#     text = re.sub(r'[\r\n]+', ' ', text)
#     text = re.sub(r'\s+', ' ', text)

#     # ---------------------------------------------------------
#     # FIX OCR DATE ISSUES
#     # ---------------------------------------------------------

#     # 21107/1440 -> 21/07/1440
#     # 1209/1440 -> 12/09/1440
#     text = re.sub(
#         r'(?<!\d)(\d{2})(\d{2})/(\d{4})(?!\d)',
#         lambda m: f"{m.group(1)}/{m.group(2)}/{m.group(3)}",
#         text
#     )

#     # Extra OCR corruption handling
#     # 21107/1440 -> 21/07/1440
#     text = re.sub(
#         r'(?<!\d)(\d{2})1(\d{2})/(\d{4})(?!\d)',
#         r'\1/\2/\3',
#         text
#     )

#     # OCR fixes:
#     # (I 7/05/20192 -> 17/05/2019
#     # I 7/05/20192 -> 17/05/2019
#     text = re.sub(
#         r'[\(\[]?[I|l]\s*(\d{1,2}/\d{2}/\d{4})\d?',
#         lambda m: "1" + m.group(1),
#         text
#     )

#     # ---------------------------------------------------------
#     # DEFAULT STRUCTURE
#     # ---------------------------------------------------------
#     meta = {
#         "document_code": "N/A",

#         "authority": {
#             "name": "N/A",
#             "short_name": "N/A"
#         },

#         "document": {
#             "type": "N/A",
#             "title": "N/A",
#             "version": "N/A"
#         },

#         "approval": {
#             "board_number": "N/A",
#             "hijri_date": "N/A",
#             "gregorian_date": "N/A"
#         },

#         "official_gazette_publication": {
#             "hijri_date": "N/A",
#             "gregorian_date": "N/A"
#         },

#         "legal_note": "N/A"
#     }

#     # ---------------------------------------------------------
#     # DOCUMENT CODE
#     # ---------------------------------------------------------
#     code_match = re.search(
#         r'\b\d{2}-\d{2}-\d{2}-\d{3}\b',
#         text
#     )

#     if code_match:
#         meta["document_code"] = code_match.group(0)

#     # ---------------------------------------------------------
#     # AUTHORITY
#     # ---------------------------------------------------------
#     authority_match = re.search(
#         r'Saudi Standards,\s*Metrology and Quality Organization',
#         text,
#         re.IGNORECASE
#     )

#     if authority_match:
#         meta["authority"]["name"] = authority_match.group(0)

#     # ---------------------------------------------------------
#     # SHORT NAME
#     # ---------------------------------------------------------
#     if re.search(r'\bSASO\b', text):
#         meta["authority"]["short_name"] = "SASO"

#     # ---------------------------------------------------------
#     # TITLE
#     # ---------------------------------------------------------
#     title_match = re.search(
#         r'(Technical Regulations?\s+for\s+.*?)(?='
#         r'This regulation was approved|'
#         r'This Technical Regulation was approved|'
#         r'Published in|'
#         r'Version|'
#         r'Note:'
#         r')',
#         text,
#         re.IGNORECASE
#     )

#     if title_match:
#         meta["document"]["title"] = title_match.group(1).strip()
#         meta["document"]["type"] = "Technical Regulation"

#     # ---------------------------------------------------------
#     # APPROVAL DETAILS
#     # ---------------------------------------------------------
#     approval_match = re.search(
#         r'No\.?\s*\((\d+)\)\s*.*?held on\s*'
#         r'(\d{2}/\d{2}/\d{4})'
#         r'.*?'
#         r'(\d{2}/\d{2}/\d{4})',
#         text,
#         re.IGNORECASE
#     )

#     if approval_match:
#         meta["approval"]["board_number"] = approval_match.group(1)
#         meta["approval"]["hijri_date"] = approval_match.group(2)
#         meta["approval"]["gregorian_date"] = approval_match.group(3)

#     # ---------------------------------------------------------
#     # OFFICIAL GAZETTE
#     # ---------------------------------------------------------
#     gazette_match = re.search(
#         r'Published in(?: the)? Official Gazette on\s*'
#         r'(\d{2}/\d{2}/\d{4})'
#         r'.*?'
#         r'(\d{2}/\d{2}/\d{4})',
#         text,
#         re.IGNORECASE
#     )

#     if gazette_match:
#         meta["official_gazette_publication"]["hijri_date"] = gazette_match.group(1)
#         meta["official_gazette_publication"]["gregorian_date"] = gazette_match.group(2)

#     # ---------------------------------------------------------
#     # VERSION
#     # ---------------------------------------------------------
#     version_match = re.search(
#         r'Version\s*\(?(\d+)\)?',
#         text,
#         re.IGNORECASE
#     )

#     if version_match:
#         meta["document"]["version"] = version_match.group(1)

#     # ---------------------------------------------------------
#     # LEGAL NOTE
#     # ---------------------------------------------------------
#     note_match = re.search(
#         r'Note\s*:?\s*(Only the Arabic version.*?translation)',
#         text,
#         re.IGNORECASE
#     )

#     if note_match:
#         meta["legal_note"] = note_match.group(1).strip()

#     return meta


import re
from typing import Dict


def extract_tr_cover_metadata(raw_text: str) -> Dict:
    """
    Generic extractor for:
    - SASO Technical Regulations
    - GSO Technical Regulations
    - GCC Technical Regulations

    Missing fields are returned as 'N/A'
    """

    # ---------------------------------------------------------
    # CLEAN TEXT
    # ---------------------------------------------------------
    text = raw_text

    text = re.sub(r'[\r\n]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    # ---------------------------------------------------------
    # FIX OCR DATE ISSUES
    # ---------------------------------------------------------

    # 21107/1440 -> 21/07/1440
    # 1209/1440 -> 12/09/1440
    text = re.sub(
        r'(?<!\d)(\d{2})(\d{2})/(\d{4})(?!\d)',
        lambda m: f"{m.group(1)}/{m.group(2)}/{m.group(3)}",
        text
    )

    # Extra OCR corruption handling
    # 21107/1440 -> 21/07/1440
    text = re.sub(
        r'(?<!\d)(\d{2})1(\d{2})/(\d{4})(?!\d)',
        r'\1/\2/\3',
        text
    )

    # OCR fixes:
    # (I 7/05/20192 -> 17/05/2019
    # I 7/05/20192 -> 17/05/2019
    text = re.sub(
        r'[\(\[]?[I|l]\s*(\d{1,2}/\d{2}/\d{4})\d?',
        lambda m: "1" + m.group(1),
        text
    )

    # ---------------------------------------------------------
    # DEFAULT STRUCTURE
    # ---------------------------------------------------------
    meta = {
        "document_code": "N/A",

        "authority": {
            "name": "N/A",
            "short_name": "N/A"
        },

        "document": {
            "type": "N/A",
            "title": "N/A",
            "version": "N/A",
            "issue_date": "N/A"
        },

        "approval": {
            "board_number": "N/A",
            "hijri_date": "N/A",
            "gregorian_date": "N/A"
        },

        "official_gazette_publication": {
            "hijri_date": "N/A",
            "gregorian_date": "N/A"
        },

        "legal_note": "N/A"
    }

    # ---------------------------------------------------------
    # DOCUMENT CODE
    # ---------------------------------------------------------
    code_match = re.search(
    r'\b(?:'
    r'\d{2}-\d{2}-\d{2}-\d{3}'          # SASO style
    r'|'
    r'[A-Z]{1,5}-\d{2,10}(?:-\d{1,5})?' # GSO style
    r')\b',
    text
)

    if code_match:
        meta["document_code"] = code_match.group(0)

    # ---------------------------------------------------------
    # AUTHORITY NAME
    # ---------------------------------------------------------
    authority_patterns = [
        r'Saudi Standards,\s*Metrology and Quality Organization',
        r'GCC Standardization Organization'
    ]

    for pattern in authority_patterns:

        authority_match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if authority_match:
            meta["authority"]["name"] = authority_match.group(0)
            break

    # ---------------------------------------------------------
    # AUTHORITY SHORT NAME
    # ---------------------------------------------------------
    if re.search(r'\bSASO\b', text):
        meta["authority"]["short_name"] = "SASO"

    elif re.search(r'\bGSO\b', text):
        meta["authority"]["short_name"] = "GSO"

    # ---------------------------------------------------------
    # TITLE
    # ---------------------------------------------------------
    title_match = re.search(
    r'((?:GCC\s+)?Technical Regulations?\s+(?:on|for)\s+.*?)(?='
    r'This\s+(?:Technical\s+)?Regulation\s+(?:is|was)\s+approved|'
    r'The\s+update\s+of\s+this\s+regulation\s+was\s+approved|'
    r'Issue\s+No|'
    r'Published\s+in|'
    r'Warning|'
    r'Note:|'
    r'Version'
    r')',
    text,
    re.IGNORECASE
)

    if title_match:
        meta["document"]["title"] = title_match.group(1).strip()
        meta["document"]["type"] = "Technical Regulation"

    # ---------------------------------------------------------
    # ISSUE NUMBER / DATE
    # ---------------------------------------------------------
    issue_match = re.search(
        r'Issue\s+No\.?\s*(\d+).*?Date\s*:?\s*\(?(\d{2}[./]\d{2}[./]\d{4})\)?',
        text,
        re.IGNORECASE
    )

    if issue_match:
        meta["document"]["version"] = issue_match.group(1)
        meta["document"]["issue_date"] = issue_match.group(2)

    # ---------------------------------------------------------
    # VERSION
    # ---------------------------------------------------------
    version_match = re.search(
        r'Version\s*\(?(\d+)\)?',
        text,
        re.IGNORECASE
    )

    if version_match:
        meta["document"]["version"] = version_match.group(1)

    # ---------------------------------------------------------
    # APPROVAL DETAILS
    # ---------------------------------------------------------
    approval_match = re.search(
        r'No\.?\s*\((\d+)\)\s*.*?held on\s*'
        r'(\d{2}/\d{2}/\d{4})'
        r'.*?'
        r'(\d{2}/\d{2}/\d{4})',
        text,
        re.IGNORECASE
    )

    if approval_match:
        meta["approval"]["board_number"] = approval_match.group(1)
        meta["approval"]["hijri_date"] = approval_match.group(2)
        meta["approval"]["gregorian_date"] = approval_match.group(3)

    # ---------------------------------------------------------
    # OFFICIAL GAZETTE
    # ---------------------------------------------------------
    gazette_match = re.search(
        r'Published in(?: the)? Official Gazette on\s*'
        r'(\d{2}/\d{2}/\d{4})'
        r'.*?'
        r'(\d{2}/\d{2}/\d{4})',
        text,
        re.IGNORECASE
    )

    if gazette_match:
        meta["official_gazette_publication"]["hijri_date"] = gazette_match.group(1)
        meta["official_gazette_publication"]["gregorian_date"] = gazette_match.group(2)

    # ---------------------------------------------------------
    # LEGAL NOTE / WARNING
    # ---------------------------------------------------------
    note_match = re.search(
        r'(Only the Arabic version.*?translation)',
        text,
        re.IGNORECASE
    )

    if note_match:
        meta["legal_note"] = note_match.group(1).strip()

    return meta