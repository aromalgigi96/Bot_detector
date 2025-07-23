import requests
import random
import time

API_URL = "http://localhost:8000/api/login"

def random_attack_payload():
    # Simulate bot-like login
    payload = {
        "username": "raja",
        "password": "raja",
        "uri": "/login",
        "client_ip": f"203.0.113.{random.randint(1, 254)}",
        "timestamp": time.time(),
        "time_to_submit": round(random.uniform(0.01, 0.09), 3),  # super fast!
        "failed_login_count_last_10min": random.randint(4, 15),
        "user_agent": random.choice([
            "python-requests/2.28.1", "curl/8.5.0", "BotAgent", "Wget/1.20.3"
        ]),
    }
    # Add 78 network flow features with bot-like or random values
    for i in range(78):
        payload[f"flow_feature_{i}"] = round(random.uniform(60, 100), 2)  # High/extreme value for attack

    return payload

# Send multiple attacks
for i in range(10):  # 10 attacks
    data = random_attack_payload()
    r = requests.post(API_URL, json=data)
    print(f"Attack {i+1}: Status {r.status_code} | Response: {r.text}")
    time.sleep(0.3)  # slight delay between attempts
