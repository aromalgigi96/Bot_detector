# app/consumers/feature_extractor.py

import json
import time
from confluent_kafka import Consumer, Producer, KafkaError
from app.utils.features import extract_features

KAFKA_BROKERS = "kafka:9092"
RAW_TOPIC      = "raw-events"
FEAT_TOPIC     = "features"

def make_consumer():
    return Consumer({
        "bootstrap.servers": KAFKA_BROKERS,
        "group.id": "feature-extractor-group",
        "auto.offset.reset": "earliest"
    })

def make_producer():
    return Producer({"bootstrap.servers": KAFKA_BROKERS})

def delivery_report(err, msg):
    if err:
        print("❌ Delivery failed:", err)

def main():
    consumer = make_consumer()
    producer = make_producer()
    consumer.subscribe([RAW_TOPIC])
    print("🎧 Listening for raw-events…")

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                # ignore end-of-partition
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    print("⚠️ Kafka error:", msg.error())
                continue

            raw = json.loads(msg.value().decode("utf-8"))
            feats = extract_features(raw)

            producer.produce(
                FEAT_TOPIC,
                key=raw.get("client_ip"),
                value=json.dumps(feats).encode("utf-8"),
                callback=delivery_report
            )
            producer.poll(0)  # deliver async
    except KeyboardInterrupt:
        print("⏹️ Shutting down…")
    finally:
        consumer.close()
        producer.flush()

if __name__ == "__main__":
    main()
