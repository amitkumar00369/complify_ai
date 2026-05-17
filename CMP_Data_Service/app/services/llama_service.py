import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import json
import re

# =========================================================
# MODEL
# =========================================================

MODEL_NAME = "Qwen/Qwen2-1.5B-Instruct"
# MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"

# =========================================================
# LOAD TOKENIZER
# =========================================================

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

# =========================================================
# LOAD MODEL
# =========================================================

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    dtype=torch.float16,
    device_map="auto"
)

# =========================================================
# GENERATE RESPONSE
# =========================================================

def generate_response(prompt):

    print("Prompt:", prompt)

    messages = [
        {
            "role": "system",
            "content": "You are a helpful compliance assistant."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    # Qwen chat template
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    # tokenize
    inputs = tokenizer(
        text,
        return_tensors="pt"
    )

    # move tensors to model device
    inputs = {
        k: v.to(model.device)
        for k, v in inputs.items()
    }

    print("Input shape:", inputs["input_ids"].shape)

    # generate
    outputs = model.generate(
        **inputs,
        max_new_tokens=512,
        do_sample=False,
        pad_token_id=tokenizer.eos_token_id
    )

    # remove prompt tokens
    generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]

    # decode
    response = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True
    )

    print("LLM Response:", response)

    return response


# =========================================================
# HS CODE FUNCTION
# =========================================================

def databyhscode_usingllm(hs_code):

    print("message:", hs_code)

    prompt = f"""
You are a Saudi compliance data extraction assistant.

Input HS Code:
{hs_code}

Task:
Generate possible matching terms for this HS code.

Return ONLY valid JSON.

Required JSON format:
{{
  "hs_code": "{hs_code}",
  "product_names": [],
  "category_names": [],
  "technical_regulation_names": [],
  "standard_names": [],
  "search_keywords": []
}}

Rules:
- Product names should be short and searchable
- Include English and Arabic names if possible
- Include spelling variations and typos
- No explanation
- No markdown
- Return JSON only
"""

    output = generate_response(prompt)

    try:

        # extract JSON
       

        return output

    except Exception as e:

        print("JSON Parse Error:", e)
        print(output)

        return {}

def answerWithQuery(query, ragData):
    prompt = f"""
User Query:
{query}

Compliance Data:
{json.dumps(ragData)}

You are a Saudi compliance expert.

Answer the user professionally.

Explain:
- whether product can be sold in KSA
- applicable regulations
- standards
- required certifications
- compliance status
- next steps
"""
    output = generate_response(prompt)

    try:

        # extract JSON
       

        return output

    except Exception as e:

        print("JSON Parse Error:", e)
        print(output)

        return {}

