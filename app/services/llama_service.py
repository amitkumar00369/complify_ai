# from transformers import pipeline, AutoTokenizer
# import json
# import re

# MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"

# # load tokenizer
# tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# # load model pipeline
# generator = pipeline(
#     "text-generation",
#     model=MODEL_NAME,
#     tokenizer=tokenizer,
#     device_map="auto",
#     pad_token_id=tokenizer.eos_token_id
# )




# def generate_aliases_llm(text_chunk: str):
#     prompt = f"""
# You are an expert in extracting technical standards.

# From the text below, extract ONLY:

# - standard_number
# - standard_code
# - english_title

# Rules:
# - Ignore Arabic text
# - Ignore page numbers, footers
# - Standard code may be like:
#   ISO 1234, EN 301, SASO-ISO-17075-1, ASTM D6753
# - English title is the last meaningful English sentence before the code

# Return ONLY JSON array like:
# [
#   {{
#     "standard_number": 1,
#     "code": "ISO 1234",
#     "title_en": "example title"
#   }}
# ]

# Text:
# {text_chunk}
# """

#     response = generator(
#         prompt,
#         max_new_tokens=20,
#         temperature=0.7,
#         do_sample=True
#     )[0]["generated_text"]

#     return response.strip()

from transformers import pipeline, AutoTokenizer
import json
import re

MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

generator = pipeline(
    "text-generation",
    model=MODEL_NAME,
    tokenizer=tokenizer,
    device_map="auto",
    pad_token_id=tokenizer.eos_token_id
)


def extract_standards_llm(text_chunk: str):
    prompt = f"""
Extract structured data from the text.

Return ONLY valid JSON. No explanation.

Format:
[
  {{
    "standard_number": <int>,
    "code": "<standard code>",
    "title_en": "<english title>"
  }}
]

Rules:
- Ignore Arabic
- Ignore page numbers
- Extract only valid standards
- If nothing found → return []

TEXT:
{text_chunk}
"""

    response = generator(
        prompt,
        max_new_tokens=300,   # 🔥 important
        temperature=0.0,      # 🔥 deterministic
        do_sample=False
    )[0]["generated_text"]

    # -------------------------
    # 🔥 Extract JSON safely
    # -------------------------
    try:
        json_text = re.search(r"\[.*\]", response, re.DOTALL).group(0)
        return json.loads(json_text)
    except:
        return []