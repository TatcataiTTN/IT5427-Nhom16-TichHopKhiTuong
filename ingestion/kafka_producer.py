#!/usr/bin/env python3
"""
Kafka producer — doc warehouse Parquet that, "replay" theo thu tu thoi gian, publish
JSON vao topic rieng theo nguon (docs/03 Tuan 1 TV3 #8, Tuan 2 TV1 #9):
  file lich su (warehouse/output/weatherobs.parquet) -> producer -> topic "weatherobs.<source>"

Can Kafka broker chay truoc (xem docker-compose.kafka.yml):
  docker compose -f docker-compose.kafka.yml up -d

Chay:
  python3 ingestion/kafka_producer.py --limit 100 --speed 0  # 0 = khong delay, phat het ngay
  # Phat lai dot nang nong 4-5/2024 cua tram GHCN cho demo phat hien di thuong streaming:
  python3 ingestion/kafka_producer.py --source GHCN --start 2024-04-01 --end 2024-05-15 --limit 0
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
    parser.add_argument("--source", help="Chi phat 1 nguon (vd GHCN, ISD, ERA5)")
    parser.add_argument("--start", help="Tu ngay (YYYY-MM-DD, UTC)")
    parser.add_argument("--end", help="Den het ngay (YYYY-MM-DD, UTC)")
    parser.add_argument("--topic", help="Ghi de ten topic (mac dinh weatherobs.<source>)")
    args = parser.parse_args()

    import pandas as pd
    from kafka import KafkaProducer
    try:
        from kafka.errors import NoBrokersAvailable  # kafka-python 2.x
    except ImportError:
        from kafka.errors import KafkaError as NoBrokersAvailable  # 3.x da bo NoBrokersAvailable

    filters = [("source", "==", args.source)] if args.source else None  # partition pruning theo source
    df = pd.read_parquet(WAREHOUSE, filters=filters)
    ts = pd.to_datetime(df["timestamp_utc"], utc=True)
    if args.start:
        df = df[ts >= pd.Timestamp(args.start, tz="UTC")]
    if args.end:
        df = df[ts.loc[df.index] < pd.Timestamp(args.end, tz="UTC") + pd.Timedelta(days=1)]
    df = df.sort_values("timestamp_utc")
    if args.limit > 0:
        df = df.head(args.limit)
    print(f"Doc {len(df)} ban ghi tu warehouse (--limit {args.limit}, 0 = khong gioi han) de replay")

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
        topic = args.topic or f"weatherobs.{row['source'].lower()}"
        # NaN khong phai JSON hop le (consumer Spark/Java se loi) -> doi thanh null
        message = {k: (None if pd.isna(v) else v) for k, v in row.items()}
        producer.send(topic, value=message)
        sent += 1
        if args.speed > 0:
            time.sleep(args.speed)

    producer.flush()
    producer.close()
    print(f"Da publish {sent} message vao topic {args.topic or 'weatherobs.<source>'}.")


if __name__ == "__main__":
    main()
