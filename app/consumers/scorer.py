import json, joblib
from confluent_kafka import Consumer, Producer, KafkaError

BROKER      = "kafka:9092"
FEAT_TOPIC  = "features"
SCORE_TOPIC = "scores"

# load your saved preprocessor+model
preproc, model = joblib.load("app/models/classifier.pkl")

def make_consumer():
    return Consumer({
      "bootstrap.servers": BROKER,
      "group.id": "scorer-group",
      "auto.offset.reset": "earliest"
    })

def make_producer():
    return Producer({"bootstrap.servers": BROKER})

def main():
    c = make_consumer()
    p = make_producer()
    c.subscribe([FEAT_TOPIC])
    print("🤖 Scorer listening for feature vectors…")
    while True:
        msg = c.poll(1.0)
        if not msg:
            continue
        if msg.error():
            if msg.error().code() != KafkaError._PARTITION_EOF:
                print("⚠️ Kafka error:", msg.error())
            continue

        feats = json.loads(msg.value().decode("utf-8"))
        # assume preproc takes a 2D array
        X = preproc.transform([list(feats.values())])
        score = model.predict_proba(X)[0,1]

        out = {"client_ip": feats.get("client_ip"), "score": float(score)}
        p.produce(SCORE_TOPIC, json.dumps(out).encode("utf-8"))
        p.poll(0)

if __name__ == "__main__":
    main()
