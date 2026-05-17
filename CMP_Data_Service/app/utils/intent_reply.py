from ast import parse
import struct

from alembic.util import msg
from fastapi.concurrency import run_in_threadpool
from requests import get
from app.utils.enum import bussinesType
from app.utils import whatsapp
from app.utils.dummy_data import get_properties, get_salons, get_events,tenant_data
from app.services.tenant_service import TenatService
from app.services.agentService import AgentService
from app.services.bussiness_service import BussinessService
from app.services.lead_service import create_lead
from app.utils.savedDataByWhatsappQuery import extract_data_and_save_services
from app.utils.parser import parse_message
from app.utils.redis_session import save_session,get_session,get_last_message


                
                
def find_tenant_or_user_by_number(user_msg, tenant_number=None, sender_number=None):

    # normalize numbers
    sender_number = sender_number.split(":")[1] if sender_number and sender_number.startswith("whatsapp") else None
    tenant_number = tenant_number.split(":")[1] if tenant_number and tenant_number.startswith("whatsapp") else None

    agentNumber = tenant_number[3:]
    leadNumber = sender_number[3:]

    agentData = AgentService.findByNumberWithUserDetails(agentNumber)
    # print("agentData",agentData)
    session_id = f"{sender_number}:{tenant_number}"

    nor_msg = parse_message(user_msg)

    if not agentData:
        return "Agent not found"

    agentDatas = agentData.get("agent")
    ownerDatas = agentData.get("user")
    tenantDatas = agentData.get("tenant")
    # print("agentDatas",agentDatas)
    # print("ownerDatas",ownerDatas)  
    print("tenantDatas",tenantDatas)

    #  GET SESSION
    session = get_session(session_id) or {
        "sender_number": sender_number,
        "agent_number": tenant_number,
        "messages": []
    }

    # ADD USER MESSAGE
    session["messages"].append({
        "sender": "user",
        "message": user_msg,
        
    })

    # OWNER CASE
    if ownerDatas['phone_number'] == leadNumber:
        print("how is debug",tenantDatas.get("business_name"))
        bussinessName = bussinesType(tenantDatas.get("business_name")).name
        print("heheee",bussinessName)

        reply = f"You are owner of {bussinessName} service"

    else:
        # HANDLE NORMAL USER FLOW
        lastMessage = get_last_message(session_id)
        print("lastMessage", lastMessage)
        if lastMessage is not None:
            reply = handle_message(user_msg, sender_number, ownerDatas, tenantDatas, agentDatas,lastIntent=lastMessage )
        else:
            reply = handle_message(user_msg, sender_number, ownerDatas, tenantDatas, agentDatas,lastIntent=None)

    #  ADD BOT REPLY
    session["messages"].append({
        "sender": "bot",
        "message": reply
    })

    # STORE EXTRA DATA
    session["last_intent"] = nor_msg["intent"]
    session["last_entity"] = nor_msg["entity"]
    session["normalize_message"] = nor_msg

    #  SAVE ONCE (IMPORTANT)
    save_session(session_id, session)

    return reply
      
        
            

    



def format_list(data, entity):
    bussinessName = bussinesType(entity).name

    if not data:
        return {
            "message": """😅 No services found

👉 Try another location  
👉 Or type "menu"
""",
            "mapping": {}
        }

    msg = "Here are available services 👇\n\n"
    mapping = {}

    numbers = []   # 👈 dynamic numbers collect karne ke liye

    for i, item in enumerate(data, 1):
        msg += f"""{item["id"]}️⃣ {item['title']}
📍 {item['location']} | 💰 ₹{item['price']}

"""
        mapping[str(i)] = item["id"]
        numbers.append(str(item["id"]))   # 👈 collect numbers

    #  dynamic join
    number_text = " / ".join(numbers)

    msg += f"""👉 Reply *{number_text}* to book  
👉 Or type service name (e.g. {bussinessName})  
👉 Type "menu" to restart
"""

    return msg


# 🔥 MAIN FUNCTION (THIS WAS MISSING)
def handle_message(user_msg, user_number,ownerData,tenantData,agentData,lastIntent=None):
    # print(tenantData,agentData,ownerData)
    serviceType = tenantData.get("business_name")
    bussinessName = bussinesType(tenantData.get("business_name")).name
    

    nor_msg = parse_message(user_msg)
    print("Parsed Message:", nor_msg)
    intent = nor_msg['intent']
    entity = nor_msg['entity']
    print("Intent:", intent, "Entity:", entity,"serviceType",serviceType,"bussinessName",bussinessName)
    

    # GREETING
    if intent == "greeting" and entity == "general":
        if  "great" in user_msg.lower() or "good" in user_msg.lower() or "awesome" in user_msg.lower() or "well" in user_msg.lower() or "ok" in user_msg.lower():
            return "Thats awesome! How can I help you?"
        return f"Hello 👋! How can I help you? I am {agentData.get('name')}: {bussinessName} service provider"

    #  SEARCH FLOW
    if intent == "search" and lastIntent!="search":
        print("Search intent detected")
        # supose user has sent message give me list then i knew that from whict tenant number we message while 
        # currenly using property provider then we reply message with greeting this is ur service list
        if entity == "general" and nor_msg.get("serviceId") is None :
                data = BussinessService.findByUserId(ownerData["id"])
                return format_list(data, serviceType)
        else:
            return f" 😊 I m provider {agentData['name']} and i provide {bussinessName} services"

    #  PRICE
    if intent == "price_inquiry":
            data = []
            if nor_msg['location'] is not None and nor_msg['price'] is not None :
                data = [p for p in BussinessService.findByUserId(ownerData["id"]) if p['location'].lower() == nor_msg['location'].lower() and p['price'] < nor_msg['price'] ]
            if nor_msg['location'] is not None:
                data = [p for p in BussinessService.findByUserId(ownerData["id"]) if p['location'].lower() == nor_msg['location'].lower()]
            elif nor_msg['price'] is not None:
                data = [p for p in BussinessService.findByUserId(ownerData["id"]) if p['price']< nor_msg['price']]
            else:
                data =BussinessService.findByUserId(ownerData["id"])
            if data:
                msg = format_list(data,serviceType)
                # min_price = min([p['price'] for p in data])
                return f" Here are services\n: {msg}"
    if intent == "unknown" and lastIntent=="search":
      print("lastIntent", lastIntent)
      return handle_booking(nor_msg, user_number, agentData,ownerData,tenantData,lastIntent)
    if intent == "booking" or (intent == "unknown" and lastIntent=="booking") :
        return handle_booking(nor_msg, user_number, agentData,ownerData,tenantData,lastIntent)
        

    #  BOOKING
def handle_booking(nor_msg, user_number, agentData,ownerData,tenantData,lastIntent=None):
        serviceType = tenantData.get("business_name")
        bussinessName = bussinesType(tenantData.get("business_name")).name
        lead = None
        if nor_msg['entity'] == "general" and nor_msg.get("serviceId") is  None:
            data = BussinessService.findByUserId(ownerData["id"])
            # print("data",data)
            

            msg = format_list(data, serviceType)
            return f"Reply with number or service name to book.\n {msg}"
        #  suppose user sent just 1 in message and last intent was booking then we will book that service for user
        
        if (lastIntent == "search" or lastIntent == "booking") and nor_msg.get("serviceId") is not None:
            print("Booking with serviceId from last search")
            data = BussinessService.findById(nor_msg.get("serviceId"))
            if data:
                item_id = data['id']
                lead = create_lead(user_number, agentData["agentWhatsappNumber"],tenant_number=ownerData["phone_number"], tenant_id=ownerData["id"], serviceId=item_id,source="1")
                if lead is None:
                    nor_msg['intent'] = "search"
                    return "Sorry, there was an issue creating your booking. Please try again."
                return f"✅ Booking has been confirmed !\nLead: {lead}"
            else:
                data = BussinessService.findByUserId(ownerData["id"])
                msg = format_list(data, serviceType)
                # return f"Reply with number or service name to book.\n {msg}"
                return f"Service not found for booking. Please try again. with correct number\n {msg}"
   
       
 
    # 🟢 AVAILABILITY
        if nor_msg['intent'] == "availability":
            data = BussinessService.findByUserId(ownerData["id"])
            msg = format_list(data, serviceType)
            return f"✅ Available hai\n: \n {msg}"
        return "I don't understand 😅"