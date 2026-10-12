#!/usr/bin/env python3
"""
Kafka producer — doc warehouse Parquet that, "replay" theo thu tu thoi gian, publish
JSON vao topic rieng theo nguon (docs/03 Tuan 1 TV3 #8, Tuan 2 TV1 #9):
  file lich su (warehouse/output/weatherobs.parquet) -> producer -> topic "weatherobs.<source>"

Can Kafka broker chay truoc (xem docker-compose.kafka.yml):
  docker compose -f docker-compose.kafka.yml up -d

Chay:
  python3 ingestion/kafka_producer.py --limit 100 --speed 0  # 0 = khong delay, phat het ngay
"""
import argparse
import json
import os
import sys
import time

WAREHOUSE = os.path.join(os.path.dirname(__file__), "..", "warehouse", "output", "weatherobs.parquet")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap", default="localhost:9092")
    parser.add_argument("--limit", type=int, default=200, help="So ban ghi phat thu (tranh phat 1 trieu dong)")
    parser.add_argument("--speed", type=float, default=0.0, help="Giay cho giua moi message (0 = khong cho)")
    args = parser.parse_args()

    import pandas as pd
    from kafka import KafkaProducer
    try:
        from kafka.errors import NoBrokersAvailable  # kafka-python 2.x
    except ImportError:
        from kafka.errors import KafkaError as NoBrokersAvailable  # 3.x da bo NoBrokersAvailable

    df = pd.read_parquet(WAREHOUSE).sort_values("timestamp_utc").head(args.limit)
    print(f"Doc {len(df)} ban ghi tu warehouse (gioi han --limit {args.limit}) de replay")

    try:
        producer = KafkaProducer(
            bootstrap_servers=args.bootstrap,
            value_serializer=lambda v: json.dumps(v, default=str, allow_nan=False).encode("utf-8"),
        )
    except NoBrokersAvailable:
        print(f"LOI: khong ket noi duoc Kafka broker tai {args.bootstrap}.")
        print("Chay truoc: docker compose -f docker-compose.kafka.yml up -d")
        sys.exit(1)

    sent = 0
    for _, row in df.iterrows():
        topic = f"weatherobs.{row['source'].lower()}"
        # NaN khong phai JSON hop le (consumer Spark/Java se loi) -> doi thanh null
        message = {k: (None if pd.isna(v) else v) for k, v in row.items()}
        producer.send(topic, value=message)
        sent += 1
        if args.speed > 0:
            time.sleep(args.speed)

    producer.flush()
    producer.close()
    print(f"Da publish {sent} message vao cac topic weatherobs.<source>.")


if __name__ == "__main__":
    main()
