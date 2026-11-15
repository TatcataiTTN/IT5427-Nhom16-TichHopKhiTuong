"""
Mat do tram do loi du lieu theo vi tri, 2 tang phat hien doc lap:
  (a) tang Ingestion: so ban ghi bi gan co QC (RANGE/JUMP/GHCN_Q/ISD_QC) tai moi tram,
      doc tu cot qc_flag cua warehouse/output/weatherobs.parquet;
  (b) tang phan tich: so ca nghi_loi_du_lieu tu xac nhan cheo (anomaly_daily.parquet) + cac chuoi
      bi gan co troi cam bien (sensor_drift.parquet).
Chi tram GHCN/ISD (ERA5/NASA POWER/Open-Meteo la luoi/mo hinh, khong co co QC tram).

Chay: python3 warehouse/plot_data_error_density.py
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.expanduser("~/.claude/skills/visualization-report-maps/scripts"))
import report_style as rs
import map_helpers as mh
import fetch_boundaries as fb

HERE = os.path.dirname(__file__)
OUTDIR = os.path.join(HERE, "output")
OUT_PNG = os.path.join(HERE, "..", "report", "figures", "data_error_density.png")
EXT = {"lon_min": 92, "lon_max": 132, "lat_min": -11, "lat_max": 24}
SRC_COLOR = {"GHCN": "#2a78d6", "ISD": "#eb6834"}
DRIFT_NAME = {"48991099999": "Phnom Penh", "48940099999": "Viêng Chăn",
              "48912599999": "Cần Thơ", "THW00041018": "THW00041018"}
DRIFT_LABEL = {"troi_dan": "trôi dần", "nhay_bac": "nhảy bậc"}
DRIFT_NUM = {  # so thu tu + do lech (do) cua nhan so so voi tam vong tron
    "48991099999": (1, (-1.9, 0.9)), "48912599999": (2, (1.8, -1.4)),
    "48940099999": (3, (-1.9, 1.3)), "THW00041018": (4, (2.0, 0.6)),
}
ASEAN = ["VNM", "THA", "IDN", "MYS", "PHL", "LAO", "MMR", "KHM", "BRN", "SGP", "TLS"]


def vn(n):
    return f"{int(n):,}".replace(",", ".")


YEARS = (2020, 2024)  # cua so ket qua cua de tai: 5 nguon cung co du lieu, co ERA5 de xac nhan cheo


def load():
    loc = pd.read_parquet(os.path.join(OUTDIR, "location.parquet"))
    w = pd.read_parquet(os.path.join(OUTDIR, "weatherobs.parquet"),
                        columns=["location_id", "source", "timestamp_utc", "qc_flag"])
    w["source"] = w["source"].astype(str)
    w = w[pd.to_datetime(w["timestamp_utc"]).dt.year.between(*YEARS)]
    st = w[w["source"].isin(["GHCN", "ISD"])]
    stations = st.groupby("location_id")["source"].first().rename("src").reset_index()
    qc = st[st["qc_flag"].notna()].groupby("location_id").size().rename("n_qc")
    a = pd.read_parquet(os.path.join(OUTDIR, "anomaly_daily.parquet"),
                        columns=["location_id", "source", "date", "xac_nhan_tong_hop"])
    a = a[pd.to_datetime(a["date"]).dt.year.between(*YEARS)]
    nl = a[a["xac_nhan_tong_hop"] == "nghi_loi_du_lieu"].groupby("location_id").size().rename("n_nghi_loi")
    g = (stations.merge(loc, on="location_id").merge(qc, on="location_id", how="left")
         .merge(nl, on="location_id", how="left"))
    g[["n_qc", "n_nghi_loi"]] = g[["n_qc", "n_nghi_loi"]].fillna(0).astype(int)
    drift = pd.read_parquet(os.path.join(OUTDIR, "sensor_drift.parquet"))
    drift = drift[drift["flag"] != "on_dinh"].merge(loc[["location_id", "lat", "lon"]], on="location_id")
    return g, drift, int(len(st[st["qc_flag"].notna()]))


def basemap(ax, world):
    lat0 = (EXT["lat_min"] + EXT["lat_max"]) / 2
    ax.set_aspect(mh.aspect_for_lat(lat0))
    world[world["ISO_A3"].isin(ASEAN)].plot(ax=ax, facecolor="#eef1ea", edgecolor="#8a9479", linewidth=0.5, zorder=1)
    world[(world["CONTINENT"] == "Asia") & ~world["ISO_A3"].isin(ASEAN)].plot(
        ax=ax, facecolor="#f3f1ea", edgecolor="#ccc", linewidth=0.4, zorder=0)
    ax.set_xlim(EXT["lon_min"], EXT["lon_max"])
    ax.set_ylim(EXT["lat_min"], EXT["lat_max"])
    mh.lonlat_axes(ax, dec=0, n=4)
    rs.north_arrow(ax, x=0.58, y=0.86, color="black", size=0.06)
    rs.scalebar_deg(ax, lat0, color="black", loc=(0.05, 0.05))


def size_legend(ax, values, scale, vmax, color, title):
    handles = [Line2D([], [], marker="o", linestyle="", markerfacecolor=color, markeredgecolor="white",
                      alpha=0.8, markersize=np.sqrt(8 + scale * np.sqrt(v / vmax)), label=vn(v)) for v in values]
    return ax.legend(handles=handles, title=title, loc="lower right", fontsize=6.3, title_fontsize=6.5,
                     frameon=True, framealpha=0.92, edgecolor="#ccc", labelspacing=1.1, borderpad=0.8)


def main():
    g, drift, n_qc_total = load()
    print(f"{len(g)} tram GHCN/ISD | {n_qc_total:,} ban ghi QC | {int((g.n_qc > 0).sum())} tram co co QC | "
          f"{g.n_nghi_loi.sum()} ca nghi loi o {int((g.n_nghi_loi > 0).sum())} tram | {len(drift)} chuoi troi")
    print(g.nlargest(5, "n_qc")[["location_id", "src", "country", "n_qc"]].to_string(index=False))
    print(g.nlargest(5, "n_nghi_loi")[["location_id", "src", "country", "n_nghi_loi"]].to_string(index=False))

    rs.set_textwidth(441.02)
    rs.apply()
    world = fb.natural_earth("admin_0_countries", scale="10m", cache_dir=os.path.join(HERE, "boundaries"))
    fig, axs = plt.subplots(1, 2, figsize=(rs.TW, rs.TW * 0.62), constrained_layout=True)

    # (a) co QC tang Ingestion
    ax = axs[0]
    basemap(ax, world)
    vmax, scale = g["n_qc"].max(), 260
    zero = g[g["n_qc"] == 0]
    ax.scatter(zero["lon"], zero["lat"], s=5, c="#9a9a9a", marker="x", linewidth=0.5, zorder=3)
    for src, col in SRC_COLOR.items():
        sub = g[(g["src"] == src) & (g["n_qc"] > 0)]
        ax.scatter(sub["lon"], sub["lat"], s=8 + scale * np.sqrt(sub["n_qc"] / vmax), c=col, alpha=0.75,
                   edgecolor="white", linewidth=0.4, zorder=4)
    leg = size_legend(ax, [10, 100, int(vmax)] if vmax > 200 else [5, 50, int(vmax)], scale, vmax, "#777", "Bản ghi bị gắn cờ QC")
    ax.add_artist(leg)
    ax.legend(handles=[Line2D([], [], marker="o", linestyle="", color=c, label=s, markersize=4)
                       for s, c in SRC_COLOR.items()] +
                      [Line2D([], [], marker="x", linestyle="", color="#9a9a9a", label="0 cờ", markersize=4)],
              loc="upper right", fontsize=6.2, frameon=True, framealpha=0.92, edgecolor="#ccc")
    ax.set_title(f"(a) Tầng Ingestion 2020–2024: {vn(n_qc_total)} bản ghi\ngắn cờ QC "
                 f"tại {int((g.n_qc > 0).sum())}/{len(g)} trạm", fontsize=8.2, fontweight="bold")

    # (b) nghi loi tu xac nhan cheo + troi cam bien
    ax = axs[1]
    basemap(ax, world)
    vmax, scale = max(g["n_nghi_loi"].max(), 1), 260
    zero = g[g["n_nghi_loi"] == 0]
    ax.scatter(zero["lon"], zero["lat"], s=5, c="#9a9a9a", marker="x", linewidth=0.5, zorder=3)
    sub = g[g["n_nghi_loi"] > 0]
    ax.scatter(sub["lon"], sub["lat"], s=8 + scale * np.sqrt(sub["n_nghi_loi"] / vmax), c="#c0392b",
               alpha=0.7, edgecolor="white", linewidth=0.4, zorder=4)
    ax.scatter(drift["lon"], drift["lat"], s=150, facecolor="none", edgecolor="black", linewidth=1.1, zorder=5)
    # So thu tu ngay canh vong tron (giai thich trong chu thich LaTeX) thay cho duong dan dai cat ban do
    for _, r in drift.iterrows():
        num, (dx, dy) = DRIFT_NUM[r["location_id"]]
        print(f"  ({num}) {r['location_id']} {r['lat']:.2f},{r['lon']:.2f} {r['var']} {r['flag']}")
        ax.text(r["lon"] + dx, r["lat"] + dy, str(num), fontsize=6.5, fontweight="bold", ha="center",
                va="center", zorder=6,
                bbox=dict(boxstyle="circle,pad=0.15", facecolor="white", edgecolor="black", linewidth=0.6))
    leg = size_legend(ax, [1, 5, int(vmax)] if vmax < 30 else [1, 10, int(vmax)], scale, vmax, "#c0392b", "Ca nghi lỗi dữ liệu")
    ax.add_artist(leg)
    ax.legend(handles=[Line2D([], [], marker="o", linestyle="", markerfacecolor="none", markeredgecolor="black",
                              markersize=7, label="Trôi cảm biến (1)–(4)")],
              loc="upper right", fontsize=6.2, frameon=True, framealpha=0.92, edgecolor="#ccc")
    ax.set_title(f"(b) Tầng phân tích 2020–2024: {vn(g.n_nghi_loi.sum())} ca nghi lỗi\ntại "
                 f"{int((g.n_nghi_loi > 0).sum())} trạm, {len(drift)} chuỗi trôi cảm biến",
                 fontsize=8.2, fontweight="bold")

    rs.save(fig, OUT_PNG)
    print(f"Da ghi {OUT_PNG}")


if __name__ == "__main__":
    main()
