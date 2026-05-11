import re

from deep_translator import GoogleTranslator


class SmartTranslator:

    # ==========================================
    # REGEX PATTERNS
    # ==========================================

    ARABIC_PATTERN = re.compile(
        r'[\u0600-\u06FF\s]{3,}'
    )

    ENGLISH_PATTERN = re.compile(
        r'[a-zA-Z]{3,}'
    )

    # ==========================================
    # CHECK ARABIC
    # ==========================================

    @staticmethod
    def has_arabic(text: str) -> bool:

        return bool(
            re.search(
                r'[\u0600-\u06FF]',
                text
            )
        )

    # ==========================================
    # CHECK ENGLISH
    # ==========================================

    @staticmethod
    def has_english(text: str) -> bool:

        return bool(
            SmartTranslator.ENGLISH_PATTERN.search(
                text
            )
        )

    # ==========================================
    # EXTRACT ARABIC CHUNKS
    # ==========================================

    @staticmethod
    def extract_arabic_chunks(
        text: str
    ):

        chunks = re.findall(
            SmartTranslator.ARABIC_PATTERN,
            text
        )

        unique_chunks = []

        seen = set()

        for chunk in chunks:

            chunk = chunk.strip()

            # skip tiny garbage
            if len(chunk) < 3:
                continue

            if chunk not in seen:

                seen.add(chunk)

                unique_chunks.append(chunk)

        return unique_chunks

    # ==========================================
    # TRANSLATE SINGLE CHUNK
    # ==========================================

    @staticmethod
    def translate_chunk(
        text: str
    ) -> str:

        try:

            translated = GoogleTranslator(
                source="auto",
                target="en"
            ).translate(text)

            return translated

        except Exception as error:

            print(
                f"Translation error: {error}"
            )

            return text

    # ==========================================
    # SMART TRANSLATION
    # ==========================================

    @staticmethod
    def smart_translate(
        text: str
    ) -> str:

        if not text:
            return ""

        # ======================================
        # NO ARABIC
        # ======================================

        if not SmartTranslator.has_arabic(
            text
        ):

            return text

        # ======================================
        # EXTRACT ONLY ARABIC CHUNKS
        # ======================================

        arabic_chunks = (
            SmartTranslator.extract_arabic_chunks(
                text
            )
        )

        translated_text = text

        # ======================================
        # TRANSLATE ONLY SMALL ARABIC PARTS
        # ======================================

        for chunk in arabic_chunks:

            # skip very large chunk
            if len(chunk) > 1000:
                continue

            translated_chunk = (
                SmartTranslator.translate_chunk(
                    chunk
                )
            )

            # skip useless translations
            if (
                translated_chunk
                and translated_chunk != chunk
            ):

                translated_text = (
                    translated_text.replace(
                        chunk,
                        translated_chunk
                    )
                )

        # ======================================
        # REMOVE DUPLICATE SPACES
        # ======================================

        translated_text = re.sub(
            r'\s+',
            ' ',
            translated_text
        ).strip()

        return translated_text