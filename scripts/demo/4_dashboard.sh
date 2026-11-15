#!/bin/bash
# Kich ban 4: Dashboard Streamlit (10 panel, doc kho Parquet that). Chay nen, tu mo trinh duyet.
source "$(dirname "$0")/_env.sh"
URL="http://localhost:8501"
if curl -s -o /dev/null "$URL"; then
  echo "Dashboard da chay san: $URL"
else
  banner "Khoi dong Streamlit (log: /tmp/nhom16_dashboard.log)"
  nohup "$STREAMLIT" run dashboard/app.py --server.headless true > /tmp/nhom16_dashboard.log 2>&1 &
  for _ in $(seq 1 40); do curl -s -o /dev/null "$URL" && break; sleep 0.5; done
fi
open "$URL" 2>/dev/null || true
echo "Dung dashboard: pkill -f 'streamlit run dashboard/app.py'"
