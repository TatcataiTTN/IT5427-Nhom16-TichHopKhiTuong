"""
Unit test cho kiểm soát chất lượng ở tầng Ingestion (ingestion/parsers.py, docs/17 mục 3, 5, 6):
cờ QC của nguồn, giới hạn vật lý, nhảy giá trị, khử trùng bản tin ISD, áp suất trạm ISD, định nghĩa
nhiệt độ GHCN, gió NASA POWER quy về 10 m. Dùng file nhỏ tự tạo, có đáp án biết trước.

Chạy: pytest tests/test_quality_control.py -v
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ingestion.parsers import apply_range_checks, parse_ghcn, parse_isd, parse_nasa_power, wind_2m_to_10m

ISD_HEADER = '"STATION","DATE","REPORT_TYPE","WND","TMP","DEW","SLP","MA1"\n'


def _isd(tmp_path, rows):
    fp = tmp_path / "isd.csv"
    fp.write_text(ISD_HEADER + "".join(rows), encoding="utf-8")
    return parse_isd(str(fp))


# ---------------------------- ISD ----------------------------
def test_isd_duplicate_reports_merged_with_priority(tmp_path):
    # Cùng thời điểm: METAR (FM-15) có nhiệt độ, không có SLP; SYNOP (FM-12) có SLP và nhiệt độ hơi khác
    df = _isd(tmp_path, [
        '"S1","2024-04-30T06:00:00","FM-12","090,1,N,0030,1","+0310,1","+0240,1","10050,1","99999,9,10020,1"\n',
        '"S1","2024-04-30T06:00:00","FM-15","090,1,N,0031,1","+0300,1","+0240,1","99999,9","10060,1,99999,9"\n',
    ])
    assert len(df) == 1
    row = df.iloc[0]
    assert row["temp_c"] == 30.0           # ưu tiên METAR (FM-15)
    assert row["pressure_msl_hpa"] == 1005.0  # METAR thiếu SLP -> lấy từ SYNOP
    assert row["pressure_surface_hpa"] == 1002.0  # áp suất trạm (MA1 thành phần 3), không phải altimeter


def test_isd_bad_qc_code_removed_and_flagged(tmp_path):
    df = _isd(tmp_path, [
        '"S1","2024-01-01T00:00:00","FM-15","090,1,N,0030,1","+0280,2","+0200,1","99999,9","99999,9,99999,9"\n',
        '"S1","2024-01-01T01:00:00","FM-15","090,1,N,0030,1","+0281,1","+0200,7","99999,9","99999,9,99999,9"\n',
    ])
    assert np.isnan(df.loc[0, "temp_c"]) and "ISD_QC:temp_c=2" in df.loc[0, "qc_flag"]
    assert df.loc[1, "temp_c"] == 28.1 and np.isnan(df.loc[1, "dewpoint_c"])
    assert "ISD_QC:dewpoint_c=7" in df.loc[1, "qc_flag"]


def test_isd_physical_range_and_jump_flags(tmp_path):
    df = _isd(tmp_path, [
        '"S1","2024-01-01T00:00:00","FM-15","090,1,N,0830,1","+0300,1","+0200,1","99999,9","99999,9,99999,9"\n',
        '"S1","2024-01-01T00:30:00","FM-15","090,1,N,0030,1","+0150,1","+0100,1","99999,9","99999,9,99999,9"\n',
    ])
    assert np.isnan(df.loc[0, "wind_speed_ms"]) and "RANGE:wind_speed_ms" in df.loc[0, "qc_flag"]  # 83 m/s
    # 30°C -> 15°C trong 30 phút: gắn cờ cả 2 điểm, KHÔNG xoá giá trị
    assert all("JUMP:temp_c" in f for f in df["qc_flag"])
    assert df["temp_c"].tolist() == [30.0, 15.0]


# ---------------------------- GHCN ----------------------------
def _ghcn(tmp_path, rows):
    fp = tmp_path / "ghcn.csv"
    fp.write_text("ID,DATE,ELEMENT,DATA_VALUE,M_FLAG,Q_FLAG,S_FLAG,OBS_TIME\n" + "".join(rows), encoding="utf-8")
    return parse_ghcn(str(fp))


def test_ghcn_qflag_value_dropped_and_temp_definition_recorded(tmp_path):
    df = _ghcn(tmp_path, [
        "X1,20240101,TAVG,250,H,,S,\n",                                       # TAVG hợp lệ
        "X1,20240101,TMAX,300,,,S,\n", "X1,20240101,TMIN,220,,,S,\n",
        "X1,20240102,TAVG,999,H,O,S,\n",                                      # TAVG bị NOAA đánh dấu outlier
        "X1,20240102,TMAX,310,,,S,\n", "X1,20240102,TMIN,230,,,S,\n",
        "X1,20240103,PRCP,5000,,G,S,\n",                                      # mưa không qua QC
    ]).set_index(pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]))
    assert df.loc["2024-01-01", "temp_c"] == 25.0 and df.loc["2024-01-01", "temp_def"] == "TAVG"
    # TAVG lỗi -> dùng (TMAX+TMIN)/2 và ghi đúng định nghĩa
    assert df.loc["2024-01-02", "temp_c"] == 27.0 and df.loc["2024-01-02", "temp_def"] == "TMAX_TMIN_MID"
    assert df.loc["2024-01-02", "qc_flag"] == "GHCN_Q:TAVG=O"
    assert np.isnan(df.loc["2024-01-03", "precip_mm"]) and df.loc["2024-01-03", "qc_flag"] == "GHCN_Q:PRCP=G"


# ---------------------------- NASA POWER ----------------------------
def _nasa(tmp_path, params):
    fp = tmp_path / "nasa.json"
    fp.write_text(json.dumps({"header": {"fill_value": -999.0}, "properties": {"parameter": params}}), encoding="utf-8")
    return parse_nasa_power(str(fp), "p")


def test_nasa_prefers_ws10m_over_ws2m(tmp_path):
    df = _nasa(tmp_path, {"T2M": {"20240101": 25.0}, "WS2M": {"20240101": 2.0}, "WS10M": {"20240101": 3.1}})
    assert df.loc[0, "wind_speed_ms"] == 3.1 and pd.isna(df.loc[0, "qc_flag"])


def test_nasa_ws2m_only_converted_to_10m_and_flagged(tmp_path):
    df = _nasa(tmp_path, {"T2M": {"20240101": 25.0}, "WS2M": {"20240101": 2.0}})
    assert abs(df.loc[0, "wind_speed_ms"] - wind_2m_to_10m(2.0)) < 1e-12
    assert df.loc[0, "qc_flag"] == "WIND_2M_TO_10M"


def test_wind_log_profile_matches_nasa_own_ratio():
    # NASA POWER tự cung cấp cả WS2M và WS10M: tỷ số trung vị thật đo được 0,650 (docs/17)
    assert abs(2.0 / wind_2m_to_10m(2.0) - 0.650) < 0.005


# ---------------------------- Giới hạn vật lý chung ----------------------------
def test_apply_range_checks_sets_nan_and_keeps_row():
    df = pd.DataFrame({"temp_c": [25.0, 65.0], "rh_pct": [50.0, 120.0], "qc_flag": [np.nan, np.nan]})
    out = apply_range_checks(df)
    assert len(out) == 2 and out.loc[0, "temp_c"] == 25.0
    assert np.isnan(out.loc[1, "temp_c"]) and np.isnan(out.loc[1, "rh_pct"])
    assert out.loc[1, "qc_flag"] == "RANGE:temp_c;RANGE:rh_pct"


def test_isd_pressure_jump_flagged(tmp_path):
    # Ví dụ thật Phnom Penh 3/7/2023: 1028,6 -> 1053,6 hPa trong 3 giờ, cả hai đều "qua QC" của NOAA
    df = _isd(tmp_path, [
        '"S1","2023-07-03T02:00:00","FM-12","090,1,N,0030,1","+0280,1","+0240,1","10286,1","99999,9,99999,9"\n',
        '"S1","2023-07-03T05:00:00","FM-12","090,1,N,0030,1","+0300,1","+0240,1","10536,1","99999,9,99999,9"\n',
        '"S1","2023-07-03T11:00:00","FM-12","090,1,N,0030,1","+0300,1","+0240,1","10540,1","99999,9,99999,9"\n',
    ])
    assert all("JUMP:pressure_msl_hpa" in f for f in df["qc_flag"].iloc[:2])
    assert pd.isna(df["qc_flag"].iloc[2])          # cách 6 giờ, đổi 0,4 hPa -> không gắn cờ
