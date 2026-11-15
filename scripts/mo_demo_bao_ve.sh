#!/bin/bash
# Mo tat ca trong 1 lenh ngay khi bat dau trinh bay: slide, source code chinh, va dashboard.
# Chay tu thu muc goc repo: bash scripts/mo_demo_bao_ve.sh
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== Mo slide bao ve =="
open "slides/final-defense.pdf" 2>/dev/null || true

echo "== Mo source code chinh (VS Code, dung thu tu Entity Resolution -> Survivorship -> Anomaly -> PINN) =="
if command -v code >/dev/null 2>&1; then
  code \
    warehouse/entity_resolution.py \
    warehouse/survivorship.py \
    warehouse/build_warehouse.py \
    warehouse/anomaly_detection.py \
    model/pinn_wind_field_v2.py \
    ingestion/parsers.py \
    dashboard/app.py
else
  echo "  (khong thay lenh 'code' -- mo tay bang editor khac)"
fi

echo "== Chay Dashboard Streamlit (Ctrl+C de dung) =="
echo "  URL: http://localhost:8501"
streamlit run dashboard/app.py
