import re

from deep_translator import GoogleTranslator


class TextTranslator:

    ARABIC_PATTERN = re.compile(
        r'[\u0600-\u06FF\s]+'
    )

    @staticmethod
    def translate_to_english(text: str) -> str:
        # print("lelelelelelelel text", len(text))

        if not text:
            return ""

        try:

            arabic_parts = re.findall(
                TextTranslator.ARABIC_PATTERN,
                text
            )

            translated_text = text

            for part in arabic_parts:

                clean_part = part.strip()

                if len(clean_part) < 2:
                    continue

                translated_part = GoogleTranslator(
                    source="auto",
                    target="en"
                ).translate(clean_part)

                translated_text = translated_text.replace(
                    part,
                    translated_part
                )

            return translated_text

        except Exception as error:

            print(
                f"Translation error: {error}"
            )

            return text