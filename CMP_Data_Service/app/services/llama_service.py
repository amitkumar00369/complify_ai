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
    
    
import re





def extract_section_compliance_data(section_title, section_content):


    prompt = f"""
    ```

    You are a Senior Saudi Compliance Expert specializing in:

    * SASO
    * SABER
    * SALEEM
    * IEC
    * ISO
    * GCC Regulations
    * Technical Regulations

    Section Title:
    {section_title}

    Section Content:
    {section_content}

    Task:

    Extract ALL compliance-related information explicitly mentioned in this section.

    Rules:

    1. Return ONLY valid JSON.
    2. Do not hallucinate.
    3. If information is not present, return empty arrays.
    4. Preserve exact names.
    5. Extract all standards, documents, certificates, obligations and requirements.
    6. No explanations.
    7. No markdown.

    Required JSON Format:

    {{
    "section_title": "{section_title}",

    "covered_products": [],

    "excluded_products": [],

    "hs_codes": [],

    "standards": [
    {{
    "standard_number": "",
    "standard_name": ""
    }}
    ],

    "required_documents": [
    {{
    "document_name": "",
    "mandatory": true,
    "purpose": ""
    }}
    ],

    "certificates": [
    {{
    "certificate_name": "",
    "mandatory": true
    }}
    ],

    "supplier_obligations": [],

    "marking_requirements": [],

    "testing_requirements": [],

    "definitions": [
    {{
    "term": "",
    "definition": ""
    }}
    ],

    "conformity_assessment": {{
    "assessment_type": "",
    "certificate_type": "",
    "requirements": []
    }},

    "important_requirements": [],

    "annex_information": []
    }}

    Return JSON only.
    """

    
    output = generate_response(prompt)

    try:
        return output
    except Exception as e:
        print("JSON Parse Error:", e)
        print(output)
        return {}
def merge_section_results(results):

    final_data = {
        "hs_codes": [],
        "standards": [],
        "required_documents": [],
        "certificates": [],
        "supplier_obligations": [],
        "marking_requirements": [],
        "testing_requirements": [],
        "definitions": [],
        "important_requirements": [],
        "annex_information": [],
        "conformity_assessment": {}
    }

    for item in results:

        final_data["hs_codes"].extend(
            item.get("hs_codes", [])
        )

        final_data["standards"].extend(
            item.get("standards", [])
        )

        final_data["required_documents"].extend(
            item.get("required_documents", [])
        )

        final_data["certificates"].extend(
            item.get("certificates", [])
        )

        final_data["supplier_obligations"].extend(
            item.get("supplier_obligations", [])
        )

        final_data["marking_requirements"].extend(
            item.get("marking_requirements", [])
        )

        final_data["testing_requirements"].extend(
            item.get("testing_requirements", [])
        )

        final_data["definitions"].extend(
            item.get("definitions", [])
        )

        final_data["important_requirements"].extend(
            item.get("important_requirements", [])
        )

        final_data["annex_information"].extend(
            item.get("annex_information", [])
        )

        conformity = item.get(
            "conformity_assessment"
        )

        if conformity:

            if not final_data[
                "conformity_assessment"
            ]:

                final_data[
                    "conformity_assessment"
                ] = conformity

            else:

                final_data[
                    "conformity_assessment"
                ]["requirements"].extend(
                    conformity.get(
                        "requirements",
                        []
                    )
                )



def get_prompt_by_type(section_type,section_content):
    try:
        if section_type == "definitions":

            return f"""
            Extract definitions.

            Return JSON:

            {{
            "definitions": [
                {{
                "term": "",
                "definition": ""
                }}
            ]
            }}

            Section:
            {section_content}
            """
        if section_type == "scope":

            return f"""
        Extract:

        - covered products
        - excluded products
        - product categories

        Return JSON:

        {{
        "covered_products": [],
        "excluded_products": []
        }}

        Section:
        {section_content}
        """
        if section_type == "supplier_obligations":

            return f"""
                Extract all supplier obligations.

                Return JSON:

                {{
                "supplier_obligations": []
                }}

                Section:
                {section_content}
            """
        if section_type == "marking":
         return f"""
            Extract:

            - labels
            - warnings
            - packaging requirements
            - marking requirements

            Return JSON:

            {{
            "marking_requirements": []
            }}

            Section:
            {section_content}
            """
        if section_type == "conformity_assessment":

           if section_type == "conformity_assessment":

            return f"""

        You are a Saudi Compliance Expert.

        Analyze the conformity assessment section.

        Extract ALL compliance requirements.

        For every requirement:

        Create requirement_id
        Extract clause number
        Identify requirement type
        Extract exact document/certificate name
        Mark mandatory=true if wording contains:
        shall, must, required, mandatory

        Return ONLY valid JSON.

        JSON Format:

        {{
        "requirements": [
        {{
        "requirement_id": "",
        "clause": "",
        "type": "",
        "name": "",
        "mandatory": true
        }}
        ]
        }}

        Requirement Types:

        document
        certificate
        test_report
        declaration
        standard
        marking
        label
        technical_file
        risk_assessment

        Section:

        {section_content}

        Return JSON only.
        """
        if section_type == "annex":

            return f"""
        Extract:

        - HS Codes
        - Standards
        - Product Categories
        - Required Documents

        Return JSON:

        {{
        "hs_codes": [],

        "standards": [
            {{
                "standard_number": "",
                "standard_name": ""
            }}
        ],

        "required_documents": [],

        "annex_information": []
        }}

        Section:
        {section_content}
        """
    except Exception as e:
        print(e)
        
def extract_section_compliance_data(
    section_type,
    section_title,
    section_content
):

    prompt = get_prompt_by_type(
        section_type,
        section_content
    )

    response = generate_response(prompt)

    return json.loads(response)