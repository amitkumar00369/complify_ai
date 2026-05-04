from transformers import pipeline

# load model once (IMPORTANT)
generator = pipeline(
    "text-generation",
    model="mistralai/Mistral-7B-Instruct-v0.2",
    device_map="auto"
)

def generate_aliases_llm(products: list) -> list:
    prompt = f"""
Generate search keywords and synonyms for:
{products}

Rules:
- include typos
- short phrases only
- return JSON list

Output:
["alias1", "alias2"]
"""

    response = generator(prompt, max_new_tokens=200)[0]["generated_text"]

    try:
        start = response.find("[")
        end = response.find("]") + 1
        return list(set(eval(response[start:end])))
    except:
        return []