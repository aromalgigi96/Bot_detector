import os
import json
import asyncio
import logging

import pandas as pd
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from app.utils.features import extract_features

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("feature_extractor")

# Kafka settings from ENV or defaults
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
RAW_TOPIC = os.getenv("RAW_TOPIC", "raw-events")
FEATURES_TOPIC = os.getenv("FEATURES_TOPIC", "features")
GROUP_ID = os.getenv("FEATURE_EXTRACTOR_GROUP", "bot-detector-feature-extractor")

async def safe_start_kafka_client(client, name, retries=10, delay=5):
    for attempt in range(1, retries + 1):
        try:
            await client.start()
            logger.info(f"{name} started successfully.")
            return
        except Exception as e:
            logger.warning(f"{name} not ready ({attempt}/{retries}): {e} - retrying in {delay}s")
            await asyncio.sleep(delay)
    raise Exception(f"{name} failed to start after {retries} retries.")

async def consume_and_extract():
    consumer = AIOKafkaConsumer(
        RAW_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=GROUP_ID,
        auto_offset_reset="earliest",
    )
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

    await safe_start_kafka_client(consumer, "KafkaConsumer")
    await safe_start_kafka_client(producer, "KafkaProducer")
    logger.info(f"Listening for raw events on topic '{RAW_TOPIC}'...")

    try:
        async for msg in consumer:
            try:
                raw_json = msg.value.decode('utf-8')
                raw_event = json.loads(raw_json)
            except Exception as e:
                logger.error(f"Error parsing raw-event JSON: {e}; skipping")
                continue

            # Extract features dict
            try:
                feat_dict = extract_features(raw_event)
            except Exception as e:
                logger.error(f"Error extracting features: {e}; raw_event={raw_event}")
                continue

            # Ensure JSON serializable: convert values to built-in types
            feat_dict_clean = {k: float(v) for k, v in feat_dict.items()}
            out_bytes = json.dumps(feat_dict_clean).encode('utf-8')

            # Send to features topic
            try:
                await producer.send_and_wait(FEATURES_TOPIC, out_bytes)
                logger.debug(f"Produced features: {feat_dict_clean}")
            except Exception as e:
                logger.error(f"Error producing to {FEATURES_TOPIC}: {e}")
    finally:
        await consumer.stop()
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(consume_and_extract())