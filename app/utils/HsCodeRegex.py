# import re


# class HSCodeService:

#     @staticmethod
#     def extract_hs_row(text, hs_code):

#         text = re.sub(r'\s+', ' ', str(text))

#         target_hs = str(hs_code).strip()

#         print("TARGET:", repr(target_hs))

#         match = re.search(
#             rf'\b{re.escape(target_hs)}\b',
#             text
#         )

#         print("MATCH:", match)

#         if not match:
#             return None

#         start = max(0, match.start() - 80)

#         return text[start:match.start()+28]

import re


class HSCodeService:

    @staticmethod
    def extract_hs_row(text, hs_code):

        target_hs = str(hs_code).strip()

        # normalize spaces
        text = re.sub(r'\s+', ' ', text)

        # locate hs code
        match = re.search(
            rf'\b{re.escape(target_hs)}\b',
            text
        )

        if not match:
            return None

        # take nearby chunk
        start = max(0, match.start() - 80)
        end = min(len(text), match.end() + 28)
        chunk=text[start:match.start()+28]

        # chunk = text[start:end]

        # stop at next hs code
        next_hs = re.search(
            r'\b\d{4}\b',
            chunk[chunk.find(target_hs) + 4:]
        )

        if next_hs:
            chunk = chunk[:chunk.find(target_hs) + 4 + next_hs.start()]

        # remove previous row garbage
        lines = re.split(
            r'(?=Water|Gas|Lighting|Containers|Heaters|Cooking)',
            chunk,
            flags=re.IGNORECASE
        )

        # take best meaningful line
        best = max(lines, key=len)

        # remove hs code
        best = re.sub(
            rf'\b{target_hs}\b',
            '',
            best
        )

        # cleanup symbols
        best = re.sub(r'[-]+', ' ', best)
        best = re.sub(r'\s+', ' ', best)

        return {
            "hs_code": target_hs,
            "text": best.strip()
        }