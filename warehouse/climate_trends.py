#!/usr/bin/env python3
"""
Xu hướng khí hậu dài hạn trên chuỗi trạm GHCN (đến ~80 năm) — tách biến đổi khí hậu dài hạn khỏi
dị thường ngắn hạn (warehouse/anomaly_detection.py).

Phương pháp chuẩn trong khí hậu học (phi tham số, không giả định phân bố chuẩn, bền với outlier):
  - Kiểm định Mann-Kendall (Mann 1945, Kendall 1975) có hiệu chỉnh giá trị trùng: xu hướng có ý
    nghĩa thống kê hay không (p < 0,05, hai phía).
  - Độ dốc Sen (Sen 1968): trung vị độ dốc của mọi cặp năm -> tốc độ thay đổi, quy về /thập kỷ.
Biến theo năm: nhiệt độ trung bình năm (năm hợp lệ khi ≥ 80% số ngày có số liệu), tổng mưa ngày
ướt PRCPTOT và mưa ngày lớn nhất Rx1day (từ precip_indices_annual.parquet, đã lọc ≥ 90% ngày).
Hai giai đoạn: toàn bộ chuỗi của trạm, và giai đoạn chung 1975–2024 để so sánh công bằng giữa trạm.

Chạy:  python3 warehouse/climate_trends.py     (sau warehouse/anomaly_detection.py)
Output: warehouse/output/climate_trends.parquet, annual_series.parquet, climate_trends_summary.json
"""
import json
import os

import numpy as np
import pandas as pd

OUT = os.path.join(os.path.dirname(__file__), "output")
MIN_YEARS = 30
MIN_TEMP_COVERAGE = 0.8
ALPHA = 0.05
PERIODS = {"toan_bo": (None, None), "1975_2024": (1975, 2024)}


def mann_kendall(x) -> dict:
    """Kiểm định Mann-Kendall cho chuỗi theo thứ tự thời gian. Trả S, Var(S) (hiệu chỉnh nhóm giá trị
    trùng), Z (hiệu chỉnh liên tục) và p hai phía theo xấp xỉ chuẩn."""
    from scipy import stats
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    n = len(x)
    if n < 3:
        return {"n": n, "S": np.nan, "var_S": np.nan, "Z": np.nan, "p": np.nan}
    diff = x[None, :] - x[:, None]                 # diff[i, j] = x[j] - x[i]
    S = float(np.sign(diff[np.triu_indices(n, 1)]).sum())
    _, counts = np.unique(x, return_counts=True)
    ties = counts[counts > 1]
    var_S = (n * (n - 1) * (2 * n + 5) - (ties * (ties - 1) * (2 * ties + 5)).sum()) / 18.0
    if S > 0:
        Z = (S - 1) / np.sqrt(var_S)
    elif S < 0:
        Z = (S + 1) / np.sqrt(var_S)
    else:
        Z = 0.0
    return {"n": n, "S": S, "var_S": var_S, "Z": float(Z), "p": float(2 * (1 - stats.norm.cdf(abs(Z))))}


def sens_slope(t, x) -> float:
    """Độ dốc Sen: trung vị của (x_j − x_i) / (t_j − t_i) trên mọi cặp i < j (đơn vị x / đơn vị t)."""
    t, x = np.asarray(t, dtype=float), np.asarray(x, dtype=float)
    ok = ~(np.isnan(t) | np.isnan(x))
    t, x = t[ok], x[ok]
    if len(t) < 2:
        return np.nan
    i, j = np.triu_indices(len(t), 1)
    dt = t[j] - t[i]
    keep = dt != 0
    return float(np.median((x[j] - x[i])[keep] / dt[keep]))


def trend_table(annual: pd.DataFrame, value_cols, min_years: int = MIN_YEARS, periods: dict = PERIODS) -> pd.DataFrame:
    """annual: location_id, source, year + các cột giá trị. Trả 1 dòng/(vị trí, nguồn, biến, giai đoạn)."""
    rows = []
    for (loc, src), g in annual.groupby(["location_id", "source"]):
        for var in value_cols:
            s = g[["year", var]].dropna().sort_values("year")
            for period, (y0, y1) in periods.items():
                p = s if y0 is None else s[s["year"].between(y0, y1)]
                if len(p) < min_years:
                    continue
                mk = mann_kendall(p[var].values)
                slope = sens_slope(p["year"].values, p[var].values)
                rows.append({
                    "location_id": loc, "source": src, "var": var, "period": period,
                    "year_from": int(p["year"].min()), "year_to": int(p["year"].max()), "n_years": mk["n"],
                    "mean": float(p[var].mean()), "sen_slope_per_decade": slope * 10,
                    "mk_Z": mk["Z"], "mk_p": mk["p"],
                    "trend": ("tang" if slope > 0 else "giam") if mk["p"] < ALPHA else "khong_ro",
                })
    return pd.DataFrame(rows)


def annual_temperature(daily: pd.DataFrame, min_coverage: float = MIN_TEMP_COVERAGE) -> pd.DataFrame:
    d = daily.dropna(subset=["temp_mean"]).copy()
    d["year"] = pd.to_datetime(d["date"]).dt.year
    a = d.groupby(["location_id", "source", "year"]).agg(temp_mean_year=("temp_mean", "mean"),
                                                          n_days=("temp_mean", "size")).reset_index()
    days = np.where(pd.to_datetime(a["year"].astype(str) + "-12-31").dt.is_leap_year, 366, 365)
    return a[a["n_days"] >= min_coverage * days].drop(columns="n_days")


def main():
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from warehouse.location import build_location_table

    daily = pd.read_parquet(os.path.join(OUT, "weather_daily.parquet"),
                            columns=["location_id", "source", "date", "temp_mean"])
    daily = daily[daily["source"] == "GHCN"]
    temp = annual_temperature(daily)
    prcp = pd.read_parquet(os.path.join(OUT, "precip_indices_annual.parquet"))
    prcp = prcp[prcp["source"] == "GHCN"][["location_id", "source", "year", "PRCPTOT", "Rx1day"]]
    annual = temp.merge(prcp, on=["location_id", "source", "year"], how="outer")
    annual.to_parquet(os.path.join(OUT, "annual_series.parquet"), index=False)

    trends = trend_table(annual, ["temp_mean_year", "PRCPTOT", "Rx1day"])
    loc = build_location_table()[["location_id", "country", "lat", "lon"]]
    trends = trends.merge(loc, on="location_id", how="left")
    trends.to_parquet(os.path.join(OUT, "climate_trends.parquet"), index=False)

    summary = {}
    for (var, period), g in trends.groupby(["var", "period"]):
        summary[f"{var}|{period}"] = {
            "so_tram": int(len(g)),
            "do_doc_sen_trung_vi_moi_thap_ky": round(float(g["sen_slope_per_decade"].median()), 3),
            "so_tram_tang_co_y_nghia": int((g["trend"] == "tang").sum()),
            "so_tram_giam_co_y_nghia": int((g["trend"] == "giam").sum()),
        }
    t = trends[(trends["var"] == "temp_mean_year") & (trends["period"] == "1975_2024")]
    summary["am_len_nhanh_nhat_1975_2024"] = t.nlargest(5, "sen_slope_per_decade")[
        ["location_id", "country", "sen_slope_per_decade", "mk_p", "n_years"]].round(3).to_dict("records")
    with open(os.path.join(OUT, "climate_trends_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"{annual['location_id'].nunique()} tram GHCN, {len(annual):,} nam-tram")
    for k, v in summary.items():
        print(k, v)


if __name__ == "__main__":
    main()
