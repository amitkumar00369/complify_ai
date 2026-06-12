import random
import uuid

import hashlib
import json
def generateUserId():
    return str(uuid.uuid4())


    return str(uuid.uuid4())
def generateOtp():
    return random.randint(111111,999999)

def generateLeadId(phone_number):
    return phone_number +"lead"+ str(random.randint(111111,999999))

def generateAgentId(name):
    return name + str(random.randint(1111,9999))



def generate_rule_hash(clause):
    key_data = {
        "field": clause["field"],
        "rule_type": clause["rule_type"],
        "action": clause["action"],
        "market": clause.get("market")
    }

    return hashlib.sha256(json.dumps(key_data, sort_keys=True).encode()).hexdigest()

def generate_clause_id(standard, field, market):
    base = f"{standard}-{market}-{field}".upper().replace(" ", "")
    unique = str(uuid.uuid4())[:6]

    return f"{base}-{unique}"

Technical_Key_Title = {
    "requirements": [
        "ARTICLE (4): OBLIGATIONS OF MANUFACTURERS",
        "Article (4) Supplier s Obligations",
        "Article (4) Obligations of Supplier",
        "Article (4): Obligations of the Supplier",
        "Article (4): Requirements of Licensing the usage of the OXO Logo",
        "Article (5) Obligations of Supplier",
        "ARTICLE (8): OBLIGATIONS OF THE MANUFACTURER",
        "ARTICLE (4): OBLIGATIONS OF MANUFACTURERS",
        "Article (4) Supplier obligations",
        "Article (4) Obligations of the Supplier",
        "Article (4): Obligations of Supplier",
        "Article 4: Obligations of Supplier",
        "Article (4): Requirements for obtaining Water Rationalization Certificate for Type",
        "Article (4) Supplier Obligations Article (5) Labelling",
       "Article (4): Obligations of Supplier",
       "Article ( 4) Obligations of Supplier",
       "Article (4) Obligations of Supplier.",
       
       
       
       
        
    ],

    "standard": [
        "Annex (1-A) List of Glue and Adhesive Products and Related Standards",
                "Annex No. (2)List of Standards",
                "Annex (1-A) List of Motorcycles and Related Standards",
                "Annex (1-A)List of Lifting Machinery and Equipment Products and Related Standards",
                "Annex (1-A) List of Mobile Machinery and Heavy Duty Equipment Products and Related Standards",
                "Annex (1-A) list of portable or hand-oriented machines products,",
                "Annex (1-A) List of products of trucks and trailers protective barriers and relevant standards",
                "Annex (1-A)List of Footwear Products and their Accessories and Related Standards",
                "Annex (1-A) List of Relevant Standards",
                "Annex (1) a) List of Standards for Pipe Products and their Accessories",
                "Annex No. (1-A) List of Bricks, Tiles, Ceramics, and Sanitary Ware Products And Relevant Standards",
                "Annex (1-A) List of Cement and Concrete Products and Relevant Standards",
             "Annex (2-a) List of Products for Food Contact Tools and Equipment and Relevant Standards",
                "Annex No. (1-A) List of Insulation and Cladding Materials Products for Buildings and the Relevant Standards",
                "Annex No.(1-A) List of Metals and Metal Alloys Products for Constructions and Buildings and Relevant Standards",
                "Annex No. (1) List of Standards",
                "Annex No. (2)List of Standards",
                "Annex (1-A)List of Leather Products and Articles Thereof and Related Standards"
                
              
                
         
                 ],
        "hs_code": [
        "Annex (1-B) List of Products and Customs Coding",
        "Annex No. (1 )A List of Polyethylene and Polypropylene Products Subject to this Regulation",
        "Annex No. (2-B) List of Products and HS Codes",
        "Annex (1-B) Customs Coding List for Relevant Product Categories:",
        "Annex (1-B)List of Products and Customs Coding",
        "Annex (1-B)List of Products and Customs Coding",
        "Annex (1-B) List of HS codes for related product categories",
        "Annex (1-B) List of Products and Customs Coding",
        "Annex (1-B)List of Products and Customs Coding",
        "Annex (1) b) List of Categories of Pipe Products and Related Products",
        "Annex No. (1-B) List of Products and Customs Codes",
           "Annex (1-B) List of Custom Codes (HS Codes) for Relevant Product Categories",
           "Annex No.(1-B) List of Products and HS Codes (Custom Codes).",
           "Annex (2-b) List of Products and Customs Coding"
    ]
}
    


