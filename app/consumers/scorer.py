# app/consumers/scorer.py

import os
import json
import asyncio
import logging

import pandas as pd
import lightgbm as lgb
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scorer")

# Kafka settings
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
FEATURES_TOPIC          = os.getenv("FEATURES_TOPIC", "features")
PREDICTIONS_TOPIC       = os.getenv("PREDICTIONS_TOPIC", "predictions")
GROUP_ID                = os.getenv("SCORER_GROUP", "bot-detector-scorer")

# Model path inside container; set via Dockerfile or env
MODEL_PATH              = os.getenv("MODEL_PATH", "/app/notebooks/final_lightgbm_tuned.txt")

# List of feature names (in exact order your model expects).
FEATURE_NAMES = [
    "Dst Port", "Protocol", "Flow Duration", "Tot Fwd Pkts", "Tot Bwd Pkts",
    "TotLen Fwd Pkts", "TotLen Bwd Pkts", "Fwd Pkt Len Max", "Fwd Pkt Len Min",
    "Fwd Pkt Len Mean", "Fwd Pkt Len Std", "Bwd Pkt Len Max", "Bwd Pkt Len Min",
    "Bwd Pkt Len Mean", "Bwd Pkt Len Std", "Flow Byts/s", "Flow Pkts/s",
    "Flow IAT Mean", "Flow IAT Std", "Flow IAT Max", "Flow IAT Min", "Fwd IAT Tot",
    "Fwd IAT Mean", "Fwd IAT Std", "Fwd IAT Max", "Fwd IAT Min", "Bwd IAT Tot",
    "Bwd IAT Mean", "Bwd IAT Std", "Bwd IAT Max", "Bwd IAT Min", "Fwd PSH Flags",
    "Bwd PSH Flags", "Fwd URG Flags", "Bwd URG Flags", "Fwd Header Len",
    "Bwd Header Len", "Fwd Pkts/s", "Bwd Pkts/s", "Pkt Len Min", "Pkt Len Max",
    "Pkt Len Mean", "Pkt Len Std", "Pkt Len Var", "FIN Flag Cnt", "SYN Flag Cnt",
    "RST Flag Cnt", "PSH Flag Cnt", "ACK Flag Cnt", "URG Flag Cnt",
    "CWE Flag Count", "ECE Flag Cnt", "Down/Up Ratio", "Pkt Size Avg",
    "Fwd Seg Size Avg", "Bwd Seg Size Avg", "Fwd Byts/b Avg", "Fwd Pkts/b Avg",
    "Fwd Blk Rate Avg", "Bwd Byts/b Avg", "Bwd Pkts/b Avg", "Bwd Blk Rate Avg",
    "Subflow Fwd Pkts", "Subflow Fwd Byts", "Subflow Bwd Pkts", "Subflow Bwd Byts",
    "Init Fwd Win Byts", "Init Bwd Win Byts", "Fwd Act Data Pkts",
    "Fwd Seg Size Min", "Active Mean", "Active Std", "Active Max", "Active Min",
    "Idle Mean", "Idle Std", "Idle Max", "Idle Min"
]

async def safe_start_kafka_client(client, name, retries=10, delay=5):
    for attempt in range(1, retries + 1):
        try:
            await client.start()
            logger.info(f"{name} started successfully.")
            return
        except Exception as e:
            logger.warning(f"{name} not ready ({attempt}/{retries}): {e} - retrying in {delay}s")
            await asyncio.sleep(delay)
    raise RuntimeError(f"{name} failed to start after {retries} retries.")

async def consume_and_score():
    # 1) Load model once
    logger.info(f"Loading LightGBM model from {MODEL_PATH}...")
    try:
        booster = lgb.Booster(model_file=MODEL_PATH)
        logger.info("Model loaded.")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return

    # 2) Setup Kafka consumer & producer
    consumer = AIOKafkaConsumer(
        FEATURES_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=GROUP_ID,
        auto_offset_reset="earliest",
    )
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

    # 3) Start them safely
    await safe_start_kafka_client(consumer, "KafkaConsumer")
    await safe_start_kafka_client(producer, "KafkaProducer")
    logger.info(f"Listening for features on topic '{FEATURES_TOPIC}'...")

    try:
        async for msg in consumer:
            # 4) Parse incoming feature JSON
            try:
                feat_dict = json.loads(msg.value.decode("utf-8"))
            except Exception as e:
                logger.error(f"Error parsing features JSON: {e}; skipping")
                continue

            # 5) Build full feature vector, default missing to 0.0
            try:
                row = [ float(feat_dict.get(name, 0.0)) for name in FEATURE_NAMES ]
                df = pd.DataFrame([row], columns=FEATURE_NAMES)
            except Exception as e:
                logger.error(f"Error building DataFrame: {e}; skipping")
                continue

            # 6) Score with LightGBM
            try:
                prob = float(booster.predict(df)[0])
                label = "Attack" if prob >= 0.5 else "Benign"
            except Exception as e:
                logger.error(f"Prediction error: {e}; skipping")
                continue

            # 7) Publish result to predictions topic
            result = {"probability": prob, "label": label}
            try:
                await producer.send_and_wait(
                    PREDICTIONS_TOPIC,
                    json.dumps(result).encode("utf-8")
                )
                logger.info(f"Produced prediction: {result}")
            except Exception as e:
                logger.error(f"Error producing to {PREDICTIONS_TOPIC}: {e}")

    finally:
        await consumer.stop()
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(consume_and_score())
