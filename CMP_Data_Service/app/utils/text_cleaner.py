import re
import html
import unicodedata


class TextCleaner:

    @staticmethod
    def normalize_text(text: str) -> str:

        if not text:
            return ""

        # ==========================================
        # FORCE STRING
        # ==========================================
        text = str(text)

        # ==========================================
        # REMOVE NULL BYTE
        # ==========================================
        text = text.replace("\x00", "")

        # ==========================================
        # REMOVE CONTROL CHARACTERS
        # ==========================================
        text = ''.join(
            ch for ch in text
            if unicodedata.category(ch)[0] != "C"
            or ch in "\n\r\t"
        )

        # ==========================================
        # HTML ENTITY DECODE
        # ==========================================
        text = html.unescape(text)

        # ==========================================
        # NORMALIZE UNICODE
        # ==========================================
        text = unicodedata.normalize(
            "NFKC",
            text
        )

        # ==========================================
        # UTF SAFE
        # ==========================================
        text = text.encode(
            "utf-8",
            errors="ignore"
        ).decode("utf-8")

        # ==========================================
        # REMOVE JAVASCRIPT
        # ==========================================
        text = re.sub(
            r'javascript:void\(0\);?',
            ' ',
            text,
            flags=re.IGNORECASE
        )

        # ==========================================
        # REMOVE URLS
        # ==========================================
        text = re.sub(
            r'https?://\S+|www\.\S+',
            ' ',
            text
        )

        # ==========================================
        # REMOVE HTML TAGS
        # ==========================================
        text = re.sub(
            r'<[^>]+>',
            ' ',
            text
        )

        # ==========================================
        # REMOVE PRIVATE UNICODE ICONS
        # ==========================================
        text = re.sub(
            r'[\uf000-\uf8ff]',
            ' ',
            text
        )

        # ==========================================
        # REMOVE SPECIAL SYMBOLS
        # ==========================================
        text = re.sub(
            r'[•▪■◆►▼▲★☆✓✔✘✖©®™]',
            ' ',
            text
        )

        # ==========================================
        # KEEP SAFE CHARACTERS
        # ==========================================
        text = re.sub(
            r'[^a-zA-Z0-9\u0600-\u06FF\s\.,:/()\-_%]',
            ' ',
            text
        )

        # ==========================================
        # REMOVE EXTRA SPACES
        # ==========================================
        text = re.sub(
            r'\s+',
            ' ',
            text
        ).strip()

        return text