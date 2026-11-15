#!/bin/bash
# Kich ban 3: Kafka + Spark Structured Streaming. Phat lai dot nang nong 1/4-15/5/2024 (GHCN),
# canh bao |z| >= 2 hien dan qua cac micro-batch (tong 179, khop batch). Can Docker Desktop dang chay.
# Moi lan chay dung 1 topic moi: Spark doc tu dau topic (earliest), nen dung lai topic cu se cong don
# ban ghi cua cac lan phat truoc va so canh bao khong con la 179.
source "$(dirname "$0")/_env.sh"
if ! docker info >/dev/null 2>&1; then
  echo "Docker chua chay: mo Docker Desktop, doi bieu tuong xanh roi chay lai."; exit 1
fi
TS="$(date +%Y%m%d_%H%M%S)"
TOPIC="weatherobs.ghcn.replay.$TS"
ALERTS="/tmp/nhom16_stream_alerts_$TS.parquet"
echo "Java: $("$JAVA_HOME/bin/java" -version 2>&1 | head -1) | topic: $TOPIC"

banner "Buoc 1: bat Kafka broker"
docker compose -f docker-compose.kafka.yml up -d 2>&1 | grep -v "orphan containers"
for _ in $(seq 1 20); do nc -z localhost 9092 2>/dev/null && break; sleep 1; done

banner "Buoc 2: phat lai dot nang nong 4-5/2024 vao Kafka"
"$PY" -W ignore ingestion/kafka_producer.py --source GHCN --start 2024-04-01 --end 2024-05-15 --limit 0 \
    --topic "$TOPIC"

banner "Buoc 3: Spark Structured Streaming phat hien di thuong theo luong (${1:-60} giay, Ctrl+C de dung som)"
"$PY" warehouse/spark_streaming_anomaly.py --topic "$TOPIC" --duration "${1:-60}" --output "$ALERTS"
