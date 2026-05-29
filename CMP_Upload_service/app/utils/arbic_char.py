import re
from deep_translator import GoogleTranslator


class SmartTranslator:

    # =====================================================
    # ARABIC PART DETECTOR
    # =====================================================

    ARABIC_PART_PATTERN = re.compile(
        r'[\u0600-\u06FF]+(?:\s+[\u0600-\u06FF]+)*'
    )

    # =====================================================
    # HAS ARABIC
    # =====================================================

    @staticmethod
    def has_arabic(text: str) -> bool:

        return bool(
            re.search(
                r'[\u0600-\u06FF]',
                str(text)
            )
        )

    # =====================================================
    # HAS ENGLISH
    # =====================================================

    @staticmethod
    def has_english(text: str) -> bool:

        return bool(
            re.search(
                r'[a-zA-Z]',
                str(text)
            )
        )

    # =====================================================
    # TRANSLATE ONLY ARABIC PART
    # =====================================================

    @staticmethod
    def translate_arabic_part(
        arabic_text: str
    ) -> str:

        try:

            arabic_text = arabic_text.strip()

            # skip tiny
            if len(arabic_text) < 2:
                return arabic_text

            translated = GoogleTranslator(
                source="ar",
                target="en"
            ).translate(arabic_text)

            return translated.strip()

        except Exception as error:

            print(
                f"Translation Error: {error}"
            )

            return arabic_text

    # =====================================================
    # MAIN SMART TRANSLATE
    # =====================================================

    @staticmethod
    def smart_translate(
        text: str
    ) -> str:

        try:

            if not text:
                return ""

            text = str(text)

            # =================================================
            # NO ARABIC
            # =================================================

            if not SmartTranslator.has_arabic(
                text
            ):
                return text

            # =================================================
            # FIND ONLY ARABIC PARTS
            # =================================================

            arabic_parts = re.findall(
                SmartTranslator.ARABIC_PART_PATTERN,
                text
            )

            if not arabic_parts:
                return text

            translated_text = text

            # =================================================
            # REPLACE ONLY ARABIC
            # =================================================

            for arabic in arabic_parts:

                arabic = arabic.strip()

                # skip numbers/codes
                if re.fullmatch(
                    r'[0-9\-_\.\/]+',
                    arabic
                ):
                    continue

                translated = (
                    SmartTranslator.translate_arabic_part(
                        arabic
                    )
                )

                if (
                    translated
                    and translated != arabic
                ):

                    translated_text = (
                        translated_text.replace(
                            arabic,
                            translated
                        )
                    )

            # clean spaces
            translated_text = re.sub(
                r'\s+',
                ' ',
                translated_text
            ).strip()

            return translated_text

        except Exception as error:

            print(
                f"Smart Translation Error: {error}"
            )

            return text
    @staticmethod
    def split_text_into_chunks(text, max_chars=2000):

        paragraphs = text.split("\n")

        chunks = []

        current_chunk = ""

        for para in paragraphs:

            para = para.strip()

            if not para:
                continue

            if len(current_chunk) + len(para) < max_chars:

                current_chunk += "\n" + para

            else:

                chunks.append(current_chunk.strip())

                current_chunk = para

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks
    
    @staticmethod
    def translate_text_chunks(text):

        try:

            if not text:
                return []

            chunks = SmartTranslator.split_text_into_chunks(text)

            translated_chunks = []

            for chunk in chunks:

                try:

                    translated = GoogleTranslator(
                        source='auto',
                        target='en'
                    ).translate(chunk)

                    translated_chunks.append({
                        "arabic": chunk,
                        "english": translated
                    })

                except Exception as e:

                    print("TRANSLATION ERROR:", e)

                    translated_chunks.append({
                        "arabic": chunk,
                        "english": chunk
                    })

            return translated_chunks

        except Exception as e:

            print("MAIN TRANSLATION ERROR:", e)

            return []