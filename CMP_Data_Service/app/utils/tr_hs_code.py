import re
from typing import List, Dict


def extract_standards(raw_text: str, scope: dict) -> List[Dict]:

    # ---------------------------------------------------------
    # SCOPE EXTRACTION
    # ---------------------------------------------------------
    start_pattern = re.escape(scope["start"])

    # more stable than exact OCR string matching
    end_pattern = r'Conformity\s+Assessment\s+Form'

    match = re.search(
        rf'{start_pattern}(.*?){end_pattern}',
        raw_text,
        flags=re.DOTALL | re.IGNORECASE
    )

    if not match:
        return []

    text = match.group(1)

    # ---------------------------------------------------------
    # CLEAN TEXT
    # ---------------------------------------------------------
    text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text, flags=re.I)

    text = re.sub(r'03-03-16-156', '', text)

    text = re.sub(r'Annex No\.\s*\(\d+\)', '', text)

    text = text.replace("List of Standards", "")

    text = text.replace("Standard", "")
    text = text.replace("Title", "")

    # ---------------------------------------------------------
    # OCR FIXES
    # ---------------------------------------------------------
    fixes = {
        "CENffR": "CEN/TR",
        "0 6954": "D6954",
        "06988": "D6988",
        "05208": "D5208",
        "03826": "D3826",
        "0400 I": "D4001",
        "04001": "D4001",
        "02765": "D2765",
        "05988": "D5988",
        "1485 1": "14851",
        "20 13": "2013",
        "1 2": "12",
        "ASTMD": "ASTM D",
        "Detennination": "Determination",
        "Determ ination": "Determination",
        "ofthe": "of the",
        "II ": "11 ",
        "I ": "1 ",
        "r!r;": "",
        "p age": "",
    }

    for old, new in fixes.items():
        text = text.replace(old, new)

    # ---------------------------------------------------------
    # SPLIT LINES
    # ---------------------------------------------------------
    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    # ---------------------------------------------------------
    # PATTERNS
    # ---------------------------------------------------------
    serial_only_pattern = re.compile(r'^\d{1,3}$')

    serial_standard_pattern = re.compile(
        r'^(\d{1,3})\s+(.+)$'
    )

    results = []

    i = 0

    while i < len(lines):

        line = lines[i]

        no = None
        standard = None

        # -----------------------------------------------------
        # CASE:
        # 10 SASO GSO 1863
        # -----------------------------------------------------
        m = serial_standard_pattern.match(line)

        if m and (
            "SASO" in line or
            "ASTM" in line or
            "ISO" in line or
            "CEN" in line
        ):

            no = int(m.group(1))

            standard = m.group(2).strip()

            j = i + 1

        # -----------------------------------------------------
        # CASE:
        # 10
        # SASO GSO 1863
        # -----------------------------------------------------
        elif serial_only_pattern.match(line):

            no = int(line)

            if i + 1 >= len(lines):
                break

            standard = lines[i + 1].strip()

            j = i + 2

        else:
            i += 1
            continue

        # -----------------------------------------------------
        # CLEAN STANDARD
        # -----------------------------------------------------
        standard = re.sub(r'\s*:\s*', ':', standard)

        standard = re.sub(r'\s+', ' ', standard)

        # -----------------------------------------------------
        # TITLE EXTRACTION
        # -----------------------------------------------------
        title_lines = []

        while j < len(lines):

            next_line = lines[j]

            # stop at next serial only
            if serial_only_pattern.match(next_line):
                break

            # stop at:
            # 10 SASO GSO 1863
            m2 = serial_standard_pattern.match(next_line)

            if m2 and (
                "SASO" in next_line or
                "ASTM" in next_line or
                "ISO" in next_line or
                "CEN" in next_line
            ):
                break

            title_lines.append(next_line)

            j += 1

        title = " ".join(title_lines)

        title = re.sub(r'\s+', ' ', title)

        title = title.replace("r!r;", "")
        title = title.replace("p age", "")

        title = title.strip()

        # -----------------------------------------------------
        # SAVE
        # -----------------------------------------------------
        results.append({
            "no": no,
            "standard": standard,
            "title": title
        })

        i = j

    return results


# ---------------------------------------------------------
# EXAMPLE
# ---------------------------------------------------------

# scope = {
#     "start": "List of Standards",
#     "end": "Conformity Assessment Form"
# }

# standards = extract_standards(raw_text, scope)

# print(standards)