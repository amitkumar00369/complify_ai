import re
from app.utils.enum import entity_keywords, bussinesType


def detect_entity(msg: str):

    for entity, keywords in entity_keywords.items():
        for word in keywords:
            if re.search(rf"\b{word}\b", msg):
                return entity
    return "general"


def parse_message(message: str):
    msg = message.lower().strip()
    print("Parsing message:", msg)

    #  Intent Detection (cleaned)
    serviceId = None
    price = None
    if msg.isdigit():
        if len(msg) > 3:  # Assuming service IDs are short numbers
            price = int(msg)
        else:
            serviceId = int(msg)
     
    if any(word in msg for word in ["book", "appointment"]):
        intent = "booking"

    elif any(word in msg for word in ["price", "charge", "cost", "fee","under"]):
        intent = "price_inquiry"

    elif any(word in msg for word in ["available", "availability", "list", "show", "give","menu"]):
        intent = "search"

    elif any(word in msg for word in ["hi", "hello", "hey", "hii"]):
        intent = "greeting"

    else:
        intent = "unknown"

    # Entity Detection (dynamic )
    entity = detect_entity(msg)
    print( "entity",entity )

    # Convert to Enum (if valid)
    business_type = None
    if entity in bussinesType.__members__:
        business_type = bussinesType[entity].value   # "1", "2" etc.

    #  Location
    location = None
    locations = ["noida", "delhi", "mumbai", "bangalore"]
    for loc in locations:
        if loc in msg:
            location = loc.title()
            break

    # Service Detection
    service_map = {
        "haircut": "Haircut",
        "facial": "Facial",
        "spa": "Spa",
        "makeup": "Makeup"
    }

    service = None
    for key, val in service_map.items():
        if key in msg:
            service = val
            break

    #  Price Extract
    # price = None
    numbers = re.findall(r"\d+(?!\s*bhk)", msg)
    if numbers:
        price = int(numbers[0])

    # Name Extraction (dynamic)
    name = None
    name_patterns = {
        "real_estate": r"(\d+bhk\s\w+)",
        "salon": r"(luxury salon|style hub|style salon)",
        "entertainment": r"(music concert|startup meetup|tech talk|art exhibition)",
        "restaurants": r"(dominos|kfc|pizza hut|burger king)"
    }

    if entity in name_patterns:
        match = re.search(name_patterns[entity], msg)
        if match:
            name = match.group(1)

    # Bedrooms (only for property)
    bedrooms = None
    if entity == "real_estate":
        match = re.search(r"(\d+)bhk", msg)
        if match:
            bedrooms = int(match.group(1))

    return {
        "intent": intent,
        "entity": entity,
        "business_type": business_type,
        "price": price,
        "location": location,
        "service": service,
        "name": name,
        "bedrooms": bedrooms,
        "serviceId": serviceId
    }