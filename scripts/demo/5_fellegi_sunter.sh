#!/bin/bash
# Kich ban 5: Fellegi-Sunter + luat phu quyet tren 2.262 cap ung vien GHCN x ISD (< 1 giay),
# so sanh voi luat Haversine 5 km dang dung.
source "$(dirname "$0")/_env.sh"
banner "Fellegi-Sunter (EM) + luat phu quyet (khac nuoc, > 10 km, chenh cao > 100 m)"
"$PY" warehouse/er_fellegi_sunter.py
