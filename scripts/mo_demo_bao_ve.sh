#!/bin/bash
# Mo tat ca trong 1 lenh truoc khi trinh bay:
#   - slide (ban chieu + ban co loi noi) va bao cao PDF
#   - 7 file source chinh + kich ban demo, kich ban loi noi, hoi dap trong VS Code
#   - Dashboard Streamlit chay nen, tu mo trinh duyet
#   - moi kich ban demo (1,2,3,5,6) mot cua so Terminal san sang, nhan Enter de chay
# Chay tu bat ky dau: bash scripts/mo_demo_bao_ve.sh        (them --no-terminals de bo cac cua so Terminal)
set -u
DEMO="$(cd "$(dirname "$0")/demo" && pwd)"
source "$DEMO/_env.sh"

banner "Mo slide va bao cao"
for f in slides/final-defense.pdf slides/final-defense-notes.pdf report/final-report.pdf; do
  [ -f "$f" ] && open "$f" || echo "  thieu $f"
done

banner "Mo source code + kich ban trong VS Code"
FILES=(
  warehouse/entity_resolution.py
  warehouse/survivorship.py
  warehouse/build_warehouse.py
  warehouse/anomaly_detection.py
  model/pinn_wind_field_v2.py
  ingestion/parsers.py
  dashboard/app.py
  docs/19-kich-ban-demo.md
  slides/kich-ban-bao-ve.md
  slides/hoi-dap-bao-ve.md
)
if command -v code >/dev/null 2>&1; then
  code "$ROOT" "${FILES[@]}"
else
  echo "  khong thay lenh 'code': mo tay bang editor khac"; printf '  %s\n' "${FILES[@]}"
fi

banner "Dashboard Streamlit"
bash "$DEMO/4_dashboard.sh"

if ! docker info >/dev/null 2>&1; then
  echo -e "\n\033[1;31m[!] Docker chua chay: kich ban 3 (Kafka + Spark Streaming) se khong chay duoc. Mo Docker Desktop truoc.\033[0m"
fi

if [ "${1:-}" != "--no-terminals" ]; then
  banner "Mo san cac cua so Terminal cho tung kich ban demo"
  open_term() {  # $1 = tieu de, $2 = script
    local cmd="cd '$ROOT'; clear; printf '\\033]0;%s\\007' '$1'; echo '$1'; echo 'Lenh: bash scripts/demo/$2'; read -p 'Nhan Enter de chay...' _; bash scripts/demo/$2"
    cmd="${cmd//\\/\\\\}"; cmd="${cmd//\"/\\\"}"
    osascript -e "tell application \"Terminal\" to do script \"$cmd\"" >/dev/null
  }
  open_term "KB1 - ER + Survivorship (Ha Noi, bao Yagi 7/9/2024)" 1_er_survivorship.sh
  open_term "KB2 - PINN truong gio (~5 giay)" 2_pinn.sh
  open_term "KB3 - Kafka + Spark Streaming (can Docker)" 3_streaming.sh
  open_term "KB5 - Fellegi-Sunter + luat phu quyet" 5_fellegi_sunter.sh
  open_term "KB6 - Lien ket tram voi luoi ERA5" 6_station_grid_link.sh
  osascript -e 'tell application "Terminal" to activate' >/dev/null
fi

banner "Xong"
cat <<'EOF'
  Kich ban demo (chi tiet loi noi: docs/19-kich-ban-demo.md)
    1  bash scripts/demo/1_er_survivorship.sh [location_id] [YYYY-MM-DD]
    2  bash scripts/demo/2_pinn.sh
    3  bash scripts/demo/3_streaming.sh [so_giay]
    4  bash scripts/demo/4_dashboard.sh          -> http://localhost:8501
    5  bash scripts/demo/5_fellegi_sunter.sh
    6  bash scripts/demo/6_station_grid_link.sh
  Dung dashboard: pkill -f 'streamlit run dashboard/app.py'
EOF
