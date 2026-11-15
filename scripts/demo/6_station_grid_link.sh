#!/bin/bash
# Kich ban 6: lien ket tram voi o luoi ERA5 0,25 do thay vi gop (~11 giay): khoang cach toi tam o,
# chenh do cao, bias nhiet theo do cao (~ -5,66 C/km).
source "$(dirname "$0")/_env.sh"
banner "Lien ket 119 vi tri voi o luoi ERA5 gan nhat"
"$PY" warehouse/station_grid_link.py
