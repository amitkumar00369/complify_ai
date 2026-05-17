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
    

