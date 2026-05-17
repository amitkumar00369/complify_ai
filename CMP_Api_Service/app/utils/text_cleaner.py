import re
import html
import unicodedata


class TextCleaner:

    @staticmethod
    def normalize_text(text: str) -> str:

        if not text:
            return ""

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
        # KEEP:
        # English
        # Arabic
        # Numbers
        # Basic punctuation
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