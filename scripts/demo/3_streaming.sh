#!/bin/bash
# Kich ban 3: Kafka + Spark Structured Streaming. Phat lai dot nang nong 1/4-15/5/2024 (GHCN),
# canh bao |z| >= 2 hien dan qua cac micro-batch (tong 179, khop batch). Can Docker Desktop dang chay.
source "$(dirname "$0")/_env.sh"
if ! docker info >/dev/null 2>&1; then
  echo "Docker chua chay: mo Docker Desktop, doi bieu tuong xanh roi chay lai."; exit 1
fi
banner "Buoc 1: bat Kafka broker"
docker compose -f docker-compose.kafka.yml up -d
banner "Buoc 2: phat lai dot nang nong 4-5/2024 vao Kafka"
"$PY" ingestion/kafka_producer.py --source GHCN --start 2024-04-01 --end 2024-05-15 --limit 0 \
    --topic weatherobs.ghcn.replay
banner "Buoc 3: Spark Structured Streaming phat hien di thuong theo luong (${1:-60} giay, Ctrl+C de dung som)"
"$PY" warehouse/spark_streaming_anomaly.py --topic weatherobs.ghcn.replay --duration "${1:-60}"
