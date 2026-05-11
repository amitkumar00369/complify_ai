import re


class HSCodeService:

    HS_PATTERN = re.compile(
        r'^\d{4}$'
    )

    @staticmethod
    def extract_hs_row(
        text: str,
        hs_code: str
    ):

        if not text or not hs_code:
            return None

        target_hs = str(hs_code)[:4]

        lines = [
            re.sub(r'\s+', ' ', line).strip()
            for line in text.splitlines()
            if line.strip()
        ]

        blocks = []

        current_lines = []
        current_hs = None

        for line in lines:

            # ======================================
            # HS CODE FOUND
            # ======================================

            if HSCodeService.HS_PATTERN.match(
                line
            ):

                # save previous block
                if current_hs:

                    blocks.append({
                        "hs_code": current_hs,
                        "text": " ".join(
                            current_lines
                        ).strip()
                    })

                # start new block
                current_hs = line

                current_lines = []

            else:

                current_lines.append(line)

        # ======================================
        # LAST BLOCK
        # ======================================

        if current_hs:

            blocks.append({
                "hs_code": current_hs,
                "text": " ".join(
                    current_lines
                ).strip()
            })

        # ======================================
        # FIND TARGET
        # ======================================

        for block in blocks:

            if block["hs_code"] == target_hs:

                return block

        return None