# app/utils/features.py

import time
import math
from urllib.parse import urlparse

# Example feature extraction: adjust as needed.
# raw_event is a dict, e.g. {"client_ip": "...", "method": "GET", "uri": "/path?query", "timestamp": 123456789}
# Return: dict of feature_name: float
def extract_features(raw_event: dict) -> dict:
    """
    Given a single raw_event dictionary, compute features as a dict.
    Adjust fields & logic for your domain.
    """
    features = {}

    # Example: HTTP method one-hot or binary flags
    method = raw_event.get("method", "").upper()
    features["is_get"] = 1.0 if method == "GET" else 0.0
    features["is_post"] = 1.0 if method == "POST" else 0.0
    # You can add other methods if needed: PUT, DELETE, etc.

    # URI-based features
    uri = raw_event.get("uri", "")
    # length of path
    features["uri_length"] = float(len(uri))
    # depth = number of "/" segments (excluding query)
    try:
        path = urlparse(uri).path
        # count non-empty segments
        depth = sum(1 for seg in path.split("/") if seg)
        features["uri_depth"] = float(depth)
    except Exception:
        features["uri_depth"] = 0.0

    # Timestamp: you might compute inter-arrival if you maintain state (outside scope here).
    # For a stateless single-event example, set inter_arrival = 0 or skip.
    features["inter_arrival"] = 0.0

    # IP-based features: last octet numeric?
    client_ip = raw_event.get("client_ip", "")
    try:
        # naive: split by ".", take last octet
        octets = client_ip.strip().split(".")
        last = int(octets[-1]) if len(octets) == 4 else 0
        features["ip_last_octet"] = float(last)
    except Exception:
        features["ip_last_octet"] = 0.0

    # Add more features based on your dataset:
    # e.g. bytes sent, header counts, user-agent features, etc.
    # features["some_custom_feature"] = ...
    # For any missing field, you can set defaults.

    return features