#!/bin/bash
# Kich ban 1: Entity Resolution + Survivorship. 1 vi tri / 1 ngay -> dung 1 dong, moi bien ghi ro nguon duoc chon.
# Mac dinh: Ha Noi (VMM00048820) ngay bao Yagi 7/9/2024. Doi: bash scripts/demo/1_er_survivorship.sh <location_id> <YYYY-MM-DD>
source "$(dirname "$0")/_env.sh"
LOC="${1:-VMM00048820}"; DAY="${2:-2024-09-07}"
banner "Survivorship: $LOC ngay $DAY (ky vong: temp tu GHCN, mua va ap suat tu ERA5)"
"$PY" - "$LOC" "$DAY" <<'EOF'
import sys, pandas as pd
loc, day = sys.argv[1], sys.argv[2]
d = pd.read_parquet("warehouse/output/weatherobs_fused.parquet", filters=[("location_id", "==", loc)])
d = d[d["day"].astype(str) == day]
cols = ["location_id", "day", "temp_c", "temp_c_source_used", "temp_c_conflict",
        "precip_mm", "precip_mm_source_used", "pressure_surface_hpa", "pressure_surface_hpa_source_used"]
print(d[cols].to_string(index=False) if len(d) else "Khong co dong nao cho vi tri/ngay nay")
print(f"\nSo dong tra ve: {len(d)} (Survivorship dam bao 1 dong / vi tri / ngay)")
EOF
banner "Ghep tram GHCN-ISD (Entity Resolution, nguong 5 km)"
"$PY" - <<'EOF'
import pandas as pd
er = pd.read_parquet("warehouse/output/entity_resolution.parquet")
print(f"{len(er)} dong ket qua ghep; vai cap dau:")
print(er.head(8).to_string(index=False))
EOF
