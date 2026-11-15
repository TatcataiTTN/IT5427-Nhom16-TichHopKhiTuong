"""
5 hinh bo sung cho muc 6.8 (Phat hien di thuong khi hau) va 6.5.3 (PINN) -- tiep theo
plot_anomaly_density.py. Tat ca so lieu doc truc tiep tu warehouse/output/*.parquet va
warehouse/output/anomaly_summary.json, khong bia:
  (3) phan loai do tin cay di thuong (xac_nhan_tong_hop)   -> anomaly_confirmation_breakdown.png
  (4) di thuong theo bien vat ly (nhiet do vs ap suat)      -> anomaly_by_variable.png
  (5) phan bo do dai dot nong (heatwave_events.parquet)     -> heatwave_duration_hist.png
  (6) SPI-3 chuoi thoi gian 2 tram Mekong, nhan dot han 2019-2020 -> spi3_mekong_timeseries.png
  (7) mua cuc doan R95pTOT% trung binh theo nuoc             -> precip_r95ptot_by_country.png

Chay: python3 warehouse/plot_anomaly_extra.py
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.expanduser("~/.claude/skills/visualization-report-maps/scripts"))
import report_style as rs

OUT = os.path.join(os.path.dirname(__file__), "..", "report", "figures")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
ANOM = os.path.join(OUTPUT_DIR, "anomaly_daily.parquet")
LOC = os.path.join(OUTPUT_DIR, "location.parquet")
Y0, Y1 = 2020, 2024  # cua so ket qua: 5 nguon cung co du lieu, co ERA5 de xac nhan cheo
COUNTRY_COLOR = {
    "Vietnam": "#D55E00", "Indonesia": "#0072B2", "Thailand": "#009E73", "Malaysia": "#CC79A7",
    "Philippines": "#E69F00", "Laos": "#56B4E9", "Myanmar": "#8B6B3D", "Brunei": "#000000",
    "Cambodia": "#999933",
}


def vn(n, dec=None):
    """So kieu Viet: dau cham hang nghin, dau phay thap phan."""
    t = f"{n:,.{dec}f}" if dec is not None else f"{int(n):,}"
    return t.replace(",", "X").replace(".", ",").replace("X", ".")


def _style():
    rs.set_textwidth(441.02)
    rs.apply()


def plot_confirmation_breakdown():
    anom = pd.read_parquet(ANOM, columns=["source", "date", "flag", "xac_nhan_tong_hop"])
    anom = anom[pd.to_datetime(anom["date"]).dt.year.between(Y0, Y1)]
    # xac_nhan_tong_hop chi duoc gan cho di thuong o nguon tram (GHCN/ISD) -- ERA5/NASA
    # POWER/Open-Meteo la luoi tai phan tich, khong co "doi chung" rieng de xac nhan cheo.
    station = anom[(anom["flag"] != "binh_thuong") & anom["source"].isin(["GHCN", "ISD"])]
    cnt = station["xac_nhan_tong_hop"].value_counts()
    order = ["xac_nhan_khi_hau", "khong_doi_chung", "di_thuong_cuc_bo", "nghi_loi_du_lieu"]
    label = {
        "xac_nhan_khi_hau": "Xác nhận khí hậu thật\n(ERA5 hoặc ≥50% trạm lân cận đồng chiều)",
        "khong_doi_chung": "Không có đối chứng\n(trước 2020, chưa có ERA5/trạm lân cận)",
        "di_thuong_cuc_bo": "Dị thường cục bộ\n(có đối chứng nhưng ủng hộ yếu)",
        "nghi_loi_du_lieu": "Nghi lỗi dữ liệu/cảm biến\n(cực đoan, mọi đối chứng đều bác bỏ)",
    }
    color = {"xac_nhan_khi_hau": "#1b8a5a", "khong_doi_chung": "#9e9e9e",
            "di_thuong_cuc_bo": "#eda100", "nghi_loi_du_lieu": "#c0392b"}
    n_khong = int(cnt.get("khong_doi_chung", 0))
    order = [k for k in order if int(cnt.get(k, 0)) > 0]  # bo thanh 0 ca (vd khong_doi_chung o 2020-2024)
    vals = [int(cnt.get(k, 0)) for k in order]
    total = sum(vals)
    pct = [100 * v / total for v in vals]

    _style()
    fig, ax = plt.subplots(figsize=(rs.TW, 2.5), dpi=300)
    y = np.arange(len(order))
    bars = ax.barh(y, [max(p, 0.6) for p in pct], color=[color[k] for k in order], height=0.6,
                   edgecolor="white")  # thanh 0,3% van nhin thay duoc
    for yi, p, v in zip(y, pct, vals):
        ax.text(max(p, 0.6) + 1.2, yi, f"{vn(p, 1)}%  ({vn(v)})", va="center", fontsize=7.8)
    ax.set_yticks(y)
    ax.set_yticklabels([label[k] for k in order], fontsize=7.6)
    ax.invert_yaxis()
    ax.set_xlim(0, 112)
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_xlabel(f"% trong {vn(total)} ca bất thường/cực đoan tại trạm GHCN/ISD "
                 f"({n_khong} ca không có đối chứng)", fontsize=7.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(left=False)
    ax.grid(axis="x", linestyle=":", linewidth=0.5, alpha=0.6)
    ax.set_title(f"Phân loại độ tin cậy dị thường tại trạm bằng xác nhận chéo, {Y0}–{Y1}",
                 fontsize=9.3, fontweight="bold")
    fig.tight_layout()
    out_png = os.path.join(OUT, "anomaly_confirmation_breakdown.png")
    rs.save(fig, out_png)
    print(f"Da ghi {out_png} | tong {total:,} ca | " +
         " | ".join(f"{k}={v:,} ({p:.1f}%)" for k, v, p in zip(order, vals, pct)))


def plot_by_variable():
    anom = pd.read_parquet(ANOM, columns=["var", "date", "flag"])
    anom = anom[pd.to_datetime(anom["date"]).dt.year.between(Y0, Y1)]
    a = anom[anom["flag"] != "binh_thuong"]
    tbl = a.groupby(["var", "flag"]).size().unstack(fill_value=0).reindex(
        columns=["bat_thuong", "cuc_doan"], fill_value=0)
    var_label = {"temp_mean": "Nhiệt độ trung bình ngày\n(temp_mean)",
                "pmsl_min": "Áp suất mực nước biển\nthấp nhất ngày (pmsl_min)"}
    tbl = tbl.reindex(["temp_mean", "pmsl_min"])

    _style()
    fig, ax = plt.subplots(figsize=(rs.TW * 0.68, 2.9), dpi=300)
    y = np.arange(len(tbl))
    ax.barh(y, tbl["bat_thuong"], color="#eda100", height=0.55, label="Bất thường (|z| ≥ 2)")
    ax.barh(y, tbl["cuc_doan"], left=tbl["bat_thuong"], color="#c0392b", height=0.55,
           label="Cực đoan (|z| ≥ 3)")
    for yi, (bt, cd) in enumerate(zip(tbl["bat_thuong"], tbl["cuc_doan"])):
        ax.text(bt + cd + tbl.values.max() * 0.02, yi, vn(bt + cd), va="center",
               fontsize=8, fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels([var_label[v] for v in tbl.index], fontsize=8.2)
    ax.invert_yaxis()
    ax.set_xlim(0, tbl.values.sum(axis=1).max() * 1.18)
    ax.set_xlabel("Số ngày-trạm-nguồn bị gắn cờ", fontsize=8.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle=":", linewidth=0.5, alpha=0.6)
    ax.legend(loc="lower right", fontsize=7.3, frameon=False)
    ax.set_title("Dị thường theo biến vật lý", fontsize=9.3, fontweight="bold")
    fig.tight_layout()
    out_png = os.path.join(OUT, "anomaly_by_variable.png")
    rs.save(fig, out_png)
    print(f"Da ghi {out_png}\n{tbl}")


def plot_heatwave_duration():
    hw = pd.read_parquet(os.path.join(OUTPUT_DIR, "heatwave_events.parquet"))
    hw = hw[pd.to_datetime(hw["start"]).dt.year.between(Y0, Y1)]
    top = hw.nlargest(1, "days").iloc[0]
    print(f"  dot dai nhat: {top['location_id']} {top['source']} tu {top['start']} {top['days']} ngay | "
          f"<=4 ngay: {(hw['days'] <= 4).mean() * 100:.1f}% | >=10 ngay: {(hw['days'] >= 10).sum()}")
    _style()
    fig, ax = plt.subplots(figsize=(rs.TW, 2.9), dpi=300)
    bins = np.arange(3, hw["days"].max() + 2) - 0.5
    ax.hist(hw["days"], bins=bins, color="#d9772e", edgecolor="white", linewidth=0.5)
    ax.set_yscale("log")
    ax.set_xlabel("Độ dài đợt nóng (số ngày liên tiếp > bách phân vị 90 của nền)", fontsize=8.5)
    ax.set_ylabel("Số đợt (thang log)", fontsize=8.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", which="both", linestyle=":", linewidth=0.5, alpha=0.5)
    med, p90, mx = hw["days"].median(), hw["days"].quantile(0.9), hw["days"].max()
    ax.axvline(med, color="#333", linestyle="--", linewidth=0.9)
    ax.annotate(f"Trung vị = {med:.0f} ngày", xy=(med, ax.get_ylim()[1] * 0.6),
               fontsize=7.3, ha="left", xytext=(med + 1, ax.get_ylim()[1] * 0.6))
    ax.set_title(f"Độ dài {vn(len(hw))} đợt nóng bắt đầu trong {Y0}–{Y1} (ETCCDI TG90p), "
                f"dài nhất {int(mx)} ngày", fontsize=9, fontweight="bold")
    fig.tight_layout()
    out_png = os.path.join(OUT, "heatwave_duration_hist.png")
    rs.save(fig, out_png)
    print(f"Da ghi {out_png} | n={len(hw):,} median={med} p90={p90} max={mx}")


def plot_spi3_mekong():
    spi = pd.read_parquet(os.path.join(OUTPUT_DIR, "spi_monthly.parquet"))
    loc = pd.read_parquet(LOC)
    mekong = loc[(loc["country"].astype(str).str.contains("Thai|Cambod")) |
                ((loc["country"].astype(str).str.contains("Viet")) & (loc["lat"] < 12))]["location_id"]
    s = spi[spi["location_id"].isin(mekong) & spi["spi3"].notna()].copy()
    s["date"] = pd.to_datetime(s["period"])
    s = s[s["date"].dt.year.between(Y0, Y1)]
    print(f"  SPI-3 {Y0}-{Y1}: " + ", ".join(f"{k}: {len(g)} thang" for k, g in s.groupby("location_id")))
    name = {"VMM00048914": "Cà Mau (VMM00048914)", "VMM00048887": "Phan Thiết (VMM00048887)"}
    color = {"VMM00048914": "#0072B2", "VMM00048887": "#D55E00"}

    _style()
    fig, ax = plt.subplots(figsize=(rs.TW, 2.9), dpi=300)
    ax.axhspan(-3.2, -1, color="#f4a9a0", alpha=0.25, label="SPI-3 ≤ −1 (hạn)")
    ax.axvspan(pd.Timestamp("2020-01-01"), pd.Timestamp("2020-05-31"), color="#c0392b", alpha=0.14)
    for lid, g in s.groupby("location_id"):
        g = g.sort_values("date").set_index("date")["spi3"]
        # Ngat duong o khoang trong > 3 thang: khong noi thang qua giai doan thieu so lieu
        gap = g.index.to_series().diff().dt.days > 95
        y = g.copy()
        parts = np.cumsum(gap.values)
        first = True
        for k in np.unique(parts):
            seg = y[parts == k]
            ax.plot(seg.index, seg.values, linewidth=0.9, color=color.get(lid, "#333"),
                   marker="o" if len(seg) == 1 else None, markersize=2,
                   label=name.get(lid, lid) if first else None)
            first = False
    ax.text(pd.Timestamp("2020-06-15"), 2.75, "Đuôi đợt hạn Mekong\n2019–2020 (1–5/2020)", fontsize=7.0,
           ha="left", va="top", color="#8a2f20", fontweight="bold")
    ax.axhline(0, color="#999", linewidth=0.6)
    ax.set_xlim(pd.Timestamp(f"{Y0}-01-01") - pd.Timedelta(days=15), pd.Timestamp(f"{Y1}-12-31"))
    ax.set_ylim(-3.2, 3.0)
    ax.set_ylabel("SPI-3", fontsize=8.5)
    ax.set_xlabel("Năm", fontsize=8.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle=":", linewidth=0.5, alpha=0.5)
    ax.legend(loc="lower left", fontsize=7, frameon=True, framealpha=0.9, edgecolor="#ccc", ncol=3)
    ax.set_title(f"SPI-3 tại 2 trạm GHCN đủ chuỗi mưa trong vùng Mekong đang xét, {Y0}–{Y1}",
                 fontsize=9, fontweight="bold")
    fig.tight_layout()
    out_png = os.path.join(OUT, "spi3_mekong_timeseries.png")
    rs.save(fig, out_png)
    print(f"Da ghi {out_png} | {s['location_id'].nunique()} tram, {len(s)} thang")


def plot_precip_r95ptot_by_country():
    pidx = pd.read_parquet(os.path.join(OUTPUT_DIR, "precip_indices_annual.parquet"))
    loc = pd.read_parquet(LOC)
    pidx = pidx[pidx["year"].between(Y0, Y1)]
    print(f"  {len(pidx)} nam-vi-tri-nguon co chi so trong {Y0}-{Y1}")
    p = pidx.merge(loc[["location_id", "country"]], on="location_id")
    agg = p.groupby("country")["R95pTOT_pct"].agg(["mean", "count"]).sort_values("mean", ascending=True)
    agg = agg[agg["count"] >= 3]  # chi giu nuoc co >=3 nam-tram co chi so, tranh uoc luong tu 1-2 diem

    _style()
    fig, ax = plt.subplots(figsize=(rs.TW, 2.9), dpi=300)
    colors = [COUNTRY_COLOR.get(c, "#888") for c in agg.index]
    bars = ax.barh(agg.index, agg["mean"], color=colors, height=0.6, edgecolor="white")
    for y, (m, n) in enumerate(zip(agg["mean"], agg["count"])):
        ax.text(m + 0.6, y, f"{vn(m, 1)}%  (n={int(n)} năm-vị trí)", va="center", fontsize=7.4)
    ax.set_xlim(0, agg["mean"].max() * 1.35)
    ax.set_xlabel("R95pTOT trung bình (% tổng lượng mưa năm đến từ ngày mưa lớn, vượt bách phân vị 95)",
                 fontsize=7.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(left=False)
    ax.grid(axis="x", linestyle=":", linewidth=0.5, alpha=0.5)
    ax.set_title(f"Mức độ tập trung mưa vào ngày mưa lớn (ETCCDI R95pTOT) theo nước, {Y0}–{Y1}",
                 fontsize=9, fontweight="bold")
    fig.tight_layout()
    out_png = os.path.join(OUT, "precip_r95ptot_by_country.png")
    rs.save(fig, out_png)
    print(f"Da ghi {out_png}\n{agg}")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    plot_confirmation_breakdown()
    plot_by_variable()
    plot_heatwave_duration()
    plot_spi3_mekong()
    plot_precip_r95ptot_by_country()
