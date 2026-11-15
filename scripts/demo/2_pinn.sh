#!/bin/bash
# Kich ban 2: PINN truong gio. Huan luyen lai that (quet 4 gia tri lambda, ~5 giay), roi chi ra
# PINN dien duoc gio tai diem giu lai va phan du danh dau vi tri gio bat thuong.
source "$(dirname "$0")/_env.sh"
banner "Huan luyen PINN truong gio (quet lambda = 0; 0,01; 0,1; 1,0)"
"$PY" model/pinn_wind_field_v2.py
banner "Phan du quan trac - PINN: vi tri gio lech truong vat ly (> trung binh + 2 sigma)"
"$PY" - <<'EOF'
import pandas as pd
p = pd.read_parquet("warehouse/output/pinn_wind_field_output.parquet")
loc = pd.read_parquet("warehouse/output/location.parquet")[["location_id", "country"]]
r = p["residual_ms"]; thr = r.mean() + 2 * r.std()
print(f"{len(p)} vi tri, phan du TB {r.mean():.2f} m/s, nguong {thr:.2f} m/s")
print(p[r > thr].merge(loc, on="location_id")[["location_id", "country", "lat", "lon", "residual_ms"]]
      .round(2).to_string(index=False))
EOF
