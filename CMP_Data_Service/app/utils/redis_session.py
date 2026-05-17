import redis
import json

r = redis.Redis(host="localhost", port=6379, db=0)

def save_session(user_number, data):
    r.setex(user_number, 300, json.dumps(data))  # 5 min expiry

def get_session(user_number):
    data = r.get(user_number)
    return json.loads(data) if data else {}

def get_last_message(session_id):
    session = get_session(session_id)


    if not session:
        return None
    # print("sesssss shivam", session)

    return session.get("last_intent")  # 👈 last message