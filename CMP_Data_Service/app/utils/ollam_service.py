from ollama import chat
import json
import re


class standardExtractor:

    MODEL = "qwen2.5:3b"

    @classmethod
    def extract_standards(cls, text: str):

        prompt = f"""
You are a compliance standards extraction engine.

Extract ALL standards from the text.

Return ONLY valid JSON.

Format:

{{
  "standards": [
    {{
      "no": 1,
      "standard_code": "SASO GSO 1798",
      "english_title": "Motorcycles - General Safety Requirements"
    }}
  ]
}}

Rules:
1. Ignore Arabic text.
2. Preserve standard codes exactly.
3. Include SASO, ISO, IEC, GSO, ECE, EN standards.
4. Do not skip rows.
5. Do not merge rows.
6. No explanation.
7. JSON only.

TEXT:
{text}
"""

        response = chat(
            model=cls.MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = response["message"]["content"]

        try:
            return json.loads(content)

        except Exception:

            # remove markdown if model returns ```json
            content = re.sub(
                r"^```json|^```|```$",
                "",
                content.strip(),
                flags=re.MULTILINE
            )

            return json.loads(content)
        
StandardExtractor  = standardExtractor()