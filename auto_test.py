import requests
import random
import time

API_URL = "http://localhost:8000/api/login"

def random_attack_payload(username="attacker", password="wrongpass"):
    payload = {
        "username": username,
        "password": password,
        "uri": "/login",
        "client_ip": f"203.0.113.{random.randint(1, 254)}",
        "timestamp": time.time(),
        "time_to_submit": round(random.uniform(0.01, 0.09), 3),  # bot-fast
        "failed_login_count_last_10min": random.randint(4, 15),
        "user_agent": random.choice([
            "python-requests/2.28.1", "curl/8.5.0", "BotAgent", "Wget/1.20.3"
        ]),
    }
    # Add network features (bot-like)
    for i in range(78):
        payload[f"flow_feature_{i}"] = round(random.uniform(60, 100), 2)
    return payload

# First, send 9 "attack" logins (wrong creds, bot behavior)
for i in range(9):
    data = random_attack_payload()
    r = requests.post(API_URL, json=data)
    print(f"Attack {i+1} (wrong creds): Status {r.status_code} | Response: {r.text}")
    time.sleep(0.3)

# Now, send 1 with correct creds but bot behavior
real_user_payload = random_attack_payload(username="raja", password="raja")
r = requests.post(API_URL, json=real_user_payload)
print(f"Attack 10 (real user, bot behavior): Status {r.status_code} | Response: {r.text}")
