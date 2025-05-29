# app/utils/features.py

from typing import Dict
from collections import defaultdict

# keep state per client IP
_session_state = defaultdict(lambda: {"last_timestamp": None})

def extract_features(event: Dict) -> Dict:
    features: Dict[str, float] = {}

    # 1) HTTP method one-hot
    method = event.get("method", "GET").upper()
    features["is_get"]  = 1.0 if method == "GET" else 0.0
    features["is_post"] = 1.0 if method == "POST" else 0.0

    # 2) URI length & depth
    uri = event.get("uri", "")
    features["uri_length"] = float(len(uri))
    features["uri_depth"]  = float(max(0, len(uri.split("/")) - 1))

    # 3) Inter-arrival time
    ts = float(event.get("timestamp", 0.0))
    state = _session_state[event.get("client_ip", "")]
    last = state["last_timestamp"]
    features["inter_arrival"] = (ts - last) if last is not None else 0.0
    state["last_timestamp"] = ts

    # 4) Last octet of client IP
    try:
        octets = event.get("client_ip", "").split(".")
        features["ip_last_octet"] = float(int(octets[-1])) if len(octets)==4 else 0.0
    except:
        features["ip_last_octet"] = 0.0

    return features
