import asyncio
import json
from aiokafka import AIOKafkaProducer

# Use 'localhost:9092' if running from host, 'kafka:9092' if inside Docker
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
RAW_TOPIC = "raw-events"

sample_events = [
    {
        "method": "GET",
        "uri": "/index.html",
        "client_ip": "192.168.1.42",
        "timestamp": 1720638000
    },
    {
        "method": "POST",
        "uri": "/login",
        "client_ip": "10.0.0.5",
        "timestamp": 1720638015
    },
    {
        "method": "GET",
        "uri": "/api/data?foo=bar",
        "client_ip": "172.16.5.120",
        "timestamp": 1720638020
    }
]

async def produce():
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    try:
        for evt in sample_events:
            await producer.send_and_wait(RAW_TOPIC, json.dumps(evt).encode("utf-8"))
            print(f"Produced: {evt}")
    finally:
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(produce())
