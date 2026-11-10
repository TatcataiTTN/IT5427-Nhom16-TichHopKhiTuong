#!/usr/bin/env python3
"""
Phát hiện trôi cảm biến (sensor drift) theo thời gian — docs/03 Tuần 3 TV1 #3.

Ý tưởng (kỹ thuật đồng nhất hoá chuỗi khí hậu — homogenization với chuỗi tham chiếu):
  bias(trạm, tháng) = trung bình tháng của (giá trị trạm − ERA5 nội suy tại CÙNG vị trí, cùng ngày).
  Biến động khí hậu thật (nắng nóng, bão, El Niño...) xuất hiện ở cả trạm lẫn ERA5 nên bị triệt
  tiêu; phần còn lại trong chuỗi bias là do cảm biến/điểm đo: thay thiết bị, hỏng, trôi hiệu chuẩn,
  đổi vị trí, đô thị hoá quanh trạm.

Hai dạng lỗi, hai kiểm định phi tham số:
  - Trôi dần (drift): Mann-Kendall + độ dốc Sen trên chuỗi bias tháng (đơn vị /năm).
  - Nhảy bậc (step change): kiểm định Pettitt (1979) — điểm gãy có ý nghĩa nhất; độ lớn bước =
    trung vị bias sau điểm gãy − trung vị trước.
Gắn cờ khi có ý nghĩa thống kê (p < 0,05) VÀ đủ lớn về vật lý (ngưỡng theo biến bên dưới).

Chạy:  python3 warehouse/sensor_drift.py          (sau warehouse/anomaly_detection.py)
Output: warehouse/output/bias_monthly.parquet, sensor_drift.parquet, sensor_drift_summary.json
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from warehouse.climate_trends import mann_kendall, sens_slope

OUT = os.path.join(os.path.dirname(__file__), "output")
VARS = {"temp_mean": "°C", "pmsl_min": "hPa"}
# Ngưỡng ý nghĩa vật lý: trôi/năm và độ lớn bước nhảy
DRIFT_PER_YEAR = {"temp_mean": 0.3, "pmsl_min": 0.5}
STEP = {"temp_mean": 0.5, "pmsl_min": 1.0}
MIN_DAYS_PER_MONTH = 15
MIN_MONTHS = 24
ALPHA = 0.05


def pettitt_test(x) -> dict:
    """Kiểm định Pettitt cho 1 điểm gãy: U_t = Σ_{i<=t} Σ_{j>t} sgn(x_i − x_j), K = max|U_t|,
    p ≈ 2·exp(−6K² / (n³ + n²)). Trả chỉ số điểm gãy (phần tử cuối của đoạn trước), K, p."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < 3:
        return {"cp": None, "K": np.nan, "p": np.nan}
    sgn = np.sign(x[:, None] - x[None, :])          # sgn[i, j] = sgn(x_i − x_j)
    # U_t = tổng sgn trên khối i<=t, j>t; tính dồn: U_t = U_{t-1} + Σ_j sgn(x_t − x_j) (mọi j)
    U = np.cumsum(sgn.sum(axis=1))[:-1]
    t = int(np.argmax(np.abs(U)))
    K = float(np.abs(U[t]))
    p = float(min(1.0, 2 * np.exp(-6 * K ** 2 / (n ** 3 + n ** 2))))
    return {"cp": t, "K": K, "p": p}


def monthly_bias(daily: pd.DataFrame, var: str) -> pd.DataFrame:
    """daily: location_id, source, date, <var>. Ghép trạm (GHCN/ISD) với ERA5 cùng vị trí, cùng ngày."""
    st = daily[daily["source"].isin(["GHCN", "ISD"])][["location_id", "source", "date", var]].dropna()
    e5 = daily[daily["source"] == "ERA5"][["location_id", "date", var]].dropna().rename(columns={var: "era5"})
    m = st.merge(e5, on=["location_id", "date"])
    m["bias"] = m[var] - m["era5"]
    m["month"] = pd.to_datetime(m["date"]).dt.to_period("M")
    b = m.groupby(["location_id", "source", "month"]).agg(bias=("bias", "mean"), n_days=("bias", "size")).reset_index()
    b = b[b["n_days"] >= MIN_DAYS_PER_MONTH].copy()
    b["var"] = var
    return b


def detect_drift(bias: pd.DataFrame, var: str) -> pd.DataFrame:
    """bias: location_id, source, month (Period), bias. Trả 1 dòng/(vị trí, nguồn) với 2 kiểm định."""
    rows = []
    for (loc, src), g in bias.groupby(["location_id", "source"]):
        g = g.sort_values("month")
        if len(g) < MIN_MONTHS:
            continue
        x = g["bias"].to_numpy()
        t_years = (g["month"].dt.year + (g["month"].dt.month - 1) / 12).to_numpy()
        mk = mann_kendall(x)
        slope = sens_slope(t_years, x)
        pt = pettitt_test(x)
        cp = pt["cp"]
        step = float(np.median(x[cp + 1:]) - np.median(x[:cp + 1])) if cp is not None else np.nan
        drift_flag = (mk["p"] < ALPHA) and abs(slope) >= DRIFT_PER_YEAR[var]
        step_flag = (pt["p"] < ALPHA) and abs(step) >= STEP[var]
        rows.append({
            "location_id": loc, "source": src, "var": var, "unit": VARS[var], "n_months": len(g),
            "month_from": str(g["month"].iloc[0]), "month_to": str(g["month"].iloc[-1]),
            "bias_median": float(np.median(x)),
            "drift_per_year": slope, "drift_mk_p": mk["p"],
            "change_month": str(g["month"].iloc[cp + 1]) if cp is not None and cp + 1 < len(g) else None,
            "step": step, "step_pettitt_p": pt["p"],
            "flag": "troi_dan" if drift_flag else ("nhay_bac" if step_flag else "on_dinh"),
        })
    return pd.DataFrame(rows)


def simulate_detection(bias: pd.DataFrame, stable: pd.DataFrame, var: str, seed: int = 0) -> dict:
    """Kiểm chứng bằng mô phỏng trên chuỗi THẬT đang ổn định: tiêm (a) trôi tuyến tính gấp 2 lần
    ngưỡng/năm từ giữa chuỗi, (b) bước nhảy gấp 2 lần ngưỡng tại vị trí ngẫu nhiên; đo tỷ lệ phát
    hiện. (Không báo tỷ lệ báo nhầm ở đây: các chuỗi gốc đã được chọn là "ổn định" nên tỷ lệ đó
    luôn bằng 0 theo cách chọn, không mang thông tin.)"""
    rng = np.random.default_rng(seed)
    hit_drift = hit_step = 0
    ids = stable[stable["var"] == var][["location_id", "source"]].itertuples(index=False)
    ids = list(ids)
    for loc, src in ids:
        g = bias[(bias["location_id"] == loc) & (bias["source"] == src)].sort_values("month").copy()
        n = len(g)
        t = np.arange(n) / 12.0
        k = n // 2
        drift = g.copy()
        drift["bias"] = g["bias"].to_numpy() + np.where(np.arange(n) >= k, 2 * DRIFT_PER_YEAR[var] * (t - t[k]), 0)
        step = g.copy()
        cp = int(rng.integers(n // 4, 3 * n // 4))
        step["bias"] = g["bias"].to_numpy() + np.where(np.arange(n) >= cp, 2 * STEP[var], 0)
        hit_drift += detect_drift(drift, var)["flag"].iloc[0] != "on_dinh"
        hit_step += detect_drift(step, var)["flag"].iloc[0] != "on_dinh"
    n = max(len(ids), 1)
    return {"so_chuoi": len(ids), "ty_le_phat_hien_troi": round(hit_drift / n, 3),
            "ty_le_phat_hien_nhay_bac": round(hit_step / n, 3)}


def main():
    from warehouse.location import build_location_table
    daily = pd.read_parquet(os.path.join(OUT, "weather_daily.parquet"),
                            columns=["location_id", "source", "date"] + list(VARS))
    biases, results = [], []
    for var in VARS:
        b = monthly_bias(daily, var)
        biases.append(b)
        results.append(detect_drift(b, var))
    bias_all = pd.concat(biases, ignore_index=True)
    bias_all["month"] = bias_all["month"].astype(str)
    bias_all.to_parquet(os.path.join(OUT, "bias_monthly.parquet"), index=False)
    res = pd.concat(results, ignore_index=True).merge(
        build_location_table()[["location_id", "country"]], on="location_id", how="left")
    res.to_parquet(os.path.join(OUT, "sensor_drift.parquet"), index=False)

    flagged = res[res["flag"] != "on_dinh"].sort_values("step_pettitt_p")
    stable = res[res["flag"] == "on_dinh"]
    bias_p = bias_all.assign(month=pd.PeriodIndex(bias_all["month"], freq="M"))
    sim = {var: simulate_detection(bias_p[bias_p["var"] == var], stable, var) for var in VARS}
    summary = {
        "chuoi_kiem_tra": int(len(res)),
        "theo_co": res["flag"].value_counts().to_dict(),
        "kiem_chung_mo_phong": sim,
        "tram_bi_gan_co": flagged[["location_id", "country", "source", "var", "flag", "drift_per_year",
                                   "change_month", "step", "step_pettitt_p"]].round(3).to_dict("records"),
    }
    with open(os.path.join(OUT, "sensor_drift_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"{len(res)} chuoi (tram x bien) du >= {MIN_MONTHS} thang | {res['flag'].value_counts().to_dict()}")
    print("Mo phong tiem loi vao chuoi that dang on dinh:", sim)
    print(flagged[["location_id", "country", "source", "var", "flag", "drift_per_year", "change_month",
                   "step", "step_pettitt_p"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
