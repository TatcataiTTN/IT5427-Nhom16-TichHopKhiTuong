"""
Hai hinh moi theo yeu cau: (1) mat do diem cua di thuong khi hau theo khu vuc (ban do bong bay
tren nen ASEAN that, dung lai report_style/map_helpers/fetch_boundaries da dung cho
study_area_map.png), (2) phan bo tan suat di thuong theo thoi gian (bieu do cot chong theo nam,
tach bat_thuong/cuc_doan). Du lieu that tu warehouse/anomaly_detection.py:
  warehouse/output/anomaly_daily.parquet (1.258.424 dong, cot flag/var/date/location_id)
  warehouse/output/location.parquet (119 vi tri, lat/lon/country)
Khong bia so: moi diem/cot deu tinh truc tiep tu hai file nay.

Chay: python3 warehouse/plot_anomaly_density.py
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates
import matplotlib.ticker
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.expanduser("~/.claude/skills/visualization-report-maps/scripts"))
import report_style as rs
import map_helpers as mh
import fetch_boundaries as fb

OUT = os.path.join(os.path.dirname(__file__), "..", "report", "figures")
ANOM = os.path.join(os.path.dirname(__file__), "output", "anomaly_daily.parquet")
LOC = os.path.join(os.path.dirname(__file__), "output", "location.parquet")
Y0, Y1 = 2020, 2024  # cua so ket qua: giai doan ca 5 nguon cung co du lieu, co ERA5 de xac nhan cheo
BBOX = {"lat_min": -11, "lat_max": 23, "lon_min": 92, "lon_max": 141}
ASEAN_ISO3 = {
    "VNM": "Vietnam", "THA": "Thailand", "IDN": "Indonesia", "MYS": "Malaysia",
    "PHL": "Philippines", "LAO": "Laos", "MMR": "Myanmar", "KHM": "Cambodia",
    "BRN": "Brunei", "SGP": "Singapore", "TLS": "Timor-Leste",
}
COUNTRY_COLOR = {  # Okabe-Ito, 1 mau co dinh / nuoc, dung chung voi cac hinh khac neu can
    "Vietnam": "#D55E00", "Indonesia": "#0072B2", "Thailand": "#009E73", "Malaysia": "#CC79A7",
    "Philippines": "#E69F00", "Laos": "#56B4E9", "Myanmar": "#8B6B3D", "Brunei": "#000000",
    "Cambodia": "#999933",
}


def plot_spatial_density():
    """Ti le ngay di thuong tai moi vi tri, Y0-Y1. Dung TI LE (so ngay gan co / so gia tri co khi hau
    nen) thay vi so dem tuyet doi: vi tri co 2 nguon (tram + ERA5) tu nhien co gap doi so dem so voi
    vi tri chi co 1 nguon, nen so dem chu yeu phan anh so nguon chu khong phai mat do di thuong."""
    anom = pd.read_parquet(ANOM, columns=["location_id", "source", "date", "flag"])
    anom = anom[pd.to_datetime(anom["date"]).dt.year.between(Y0, Y1)]
    loc = pd.read_parquet(LOC)
    st = anom.groupby("location_id").agg(n_gia_tri=("flag", "size"),
                                         n_bat_thuong=("flag", lambda f: int((f != "binh_thuong").sum())))
    st["ty_le"] = 100 * st["n_bat_thuong"] / st["n_gia_tri"]
    g = loc.merge(st, on="location_id", how="inner")
    print(f"{len(g)} vi tri, tong {int(g['n_bat_thuong'].sum()):,} ngay bat-thuong/cuc-doan | ty le "
          f"min {g.ty_le.min():.2f}% trung vi {g.ty_le.median():.2f}% max {g.ty_le.max():.2f}%")
    print(g.groupby("country")["n_bat_thuong"].sum().sort_values(ascending=False).to_dict())

    rs.set_textwidth(441.02)
    rs.apply()
    world = fb.natural_earth("admin_0_countries", scale="10m",
                             cache_dir=os.path.join(os.path.dirname(__file__), "boundaries"))
    asean = world[world["ISO_A3"].isin(ASEAN_ISO3.keys())]

    fig, ax = plt.subplots(figsize=(rs.TW, rs.TW * 0.82))
    lat0 = (BBOX["lat_min"] + BBOX["lat_max"]) / 2
    ax.set_aspect(mh.aspect_for_lat(lat0))
    asean.plot(ax=ax, facecolor="#eef1ea", edgecolor="#8a9479", linewidth=0.6, zorder=1)
    others = world[(world["CONTINENT"] == "Asia") & (~world["ISO_A3"].isin(ASEAN_ISO3.keys()))]
    others.plot(ax=ax, facecolor="#f3f1ea", edgecolor="#ccc", linewidth=0.4, zorder=0)
    g = g.sort_values("ty_le")
    sc = ax.scatter(g["lon"], g["lat"], c=g["ty_le"], cmap="YlOrRd", vmin=g["ty_le"].min(),
                    vmax=g["ty_le"].max(), s=34, edgecolor="#444", linewidth=0.4, zorder=4)
    for _, r in g.nlargest(2, "ty_le").iterrows():
        ax.annotate(f"{r['location_id']}: {r['ty_le']:.1f}%".replace(".", ","), (r["lon"], r["lat"]),
                    xytext=(6, 5), textcoords="offset points", fontsize=6.3, zorder=5,
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="#bbb", linewidth=0.4))
    cb = fig.colorbar(sc, ax=ax, orientation="horizontal", fraction=0.045, pad=0.07, shrink=0.7)
    cb.set_label(f"Tỉ lệ ngày bất thường/cực đoan (|z| ≥ 2) trên tổng số giá trị, {Y0}–{Y1} (%)", fontsize=7.5)
    cb.ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.1f}".replace(".", ",")))
    cb.ax.tick_params(labelsize=7)

    ax.set_xlim(BBOX["lon_min"] - 6, BBOX["lon_max"] + 6)
    ax.set_ylim(BBOX["lat_min"] - 6, BBOX["lat_max"] + 6)
    mh.lonlat_axes(ax, dec=0, n=5)
    rs.north_arrow(ax, x=0.08, y=0.90, color="black")
    rs.scalebar_deg(ax, lat0, color="black", loc=(0.06, 0.06))
    ax.set_title(f"Mật độ dị thường khí hậu theo vị trí, {Y0}–{Y1} (119 vị trí, 5 nguồn)",
                 fontsize=9, fontweight="bold")

    out_png = os.path.join(OUT, "anomaly_spatial_density.png")
    rs.save(fig, out_png)
    print(f"Da ghi {out_png}")
    print(g.nlargest(3, "ty_le")[["location_id", "country", "n_bat_thuong", "ty_le"]].to_string(index=False))


def plot_time_distribution():
    anom = pd.read_parquet(ANOM, columns=["date", "var", "flag"])
    a = anom[anom["flag"] != "binh_thuong"].copy()
    a["date"] = pd.to_datetime(a["date"])
    a = a[a["date"].dt.year.between(Y0, Y1)]
    a["month"] = a["date"].dt.to_period("M").dt.to_timestamp()
    mo = a.groupby(["month", "var"]).size().unstack(fill_value=0).reindex(
        columns=["temp_mean", "pmsl_min"], fill_value=0)
    mo = mo.reindex(pd.date_range(f"{Y0}-01-01", f"{Y1}-12-01", freq="MS"), fill_value=0)
    print(f"{len(mo)} thang, tong {int(mo.values.sum()):,} ngay bi gan co | nhiet {int(mo.temp_mean.sum()):,} "
          f"ap suat {int(mo.pmsl_min.sum()):,}")
    tot = mo.sum(axis=1)
    print("Top 5 thang:", {k.strftime('%m/%Y'): int(v) for k, v in tot.nlargest(5).items()})

    rs.set_textwidth(441.02)
    rs.apply()
    fig, ax = plt.subplots(figsize=(rs.TW, 3.0), dpi=300)
    x = mo.index
    ax.bar(x, mo["temp_mean"], width=25, color="#d9772e", label="Nhiệt độ trung bình ngày")
    ax.bar(x, mo["pmsl_min"], width=25, bottom=mo["temp_mean"], color="#2a78d6",
          label="Áp suất mực nước biển thấp nhất ngày")
    ax.set_ylabel("Số ngày-vị-trí-nguồn bị gắn cờ", fontsize=8.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle=":", linewidth=0.5, alpha=0.6)
    ax.legend(loc="upper left", fontsize=7.2, frameon=False)
    ymax = tot.max()
    ax.set_ylim(0, ymax * 1.22)
    ax.set_ylim(0, ymax * 1.28)
    heat = mo.loc["2024-04-01"]
    ax.annotate(f"Nắng nóng 4/2024: {int(heat['temp_mean'])} ngày-vị-trí\nbất thường nhiệt độ",
               xy=(pd.Timestamp("2024-04-01"), heat.sum() + ymax * 0.01),
               xytext=(pd.Timestamp("2024-03-10"), ymax * 1.13), fontsize=6.6, ha="right", va="center",
               arrowprops=dict(arrowstyle="->", color="#333", linewidth=0.7))
    k = pd.Timestamp("2024-09-01")
    ax.annotate(f"Bão Yagi 9/2024: {int(tot[k])}\n(tháng cao nhất)".replace(",", "."), xy=(k, tot[k] + ymax * 0.01),
               xytext=(k, ymax * 1.15), fontsize=6.6, ha="center", va="center",
               arrowprops=dict(arrowstyle="->", color="#333", linewidth=0.7))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{int(v):,}".replace(",", ".")))
    ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%m/%Y"))
    ax.tick_params(axis="x", labelsize=7.5)
    ax.set_xlim(pd.Timestamp(f"{Y0}-01-01") - pd.Timedelta(days=20), pd.Timestamp(f"{Y1}-12-31"))
    ax.set_title(f"Số ngày dị thường khí hậu theo tháng, {Y0}–{Y1} (5 nguồn, |z| ≥ 2)",
                 fontsize=9.3, fontweight="bold")
    fig.tight_layout()

    out_png = os.path.join(OUT, "anomaly_time_distribution.png")
    rs.save(fig, out_png)
    print(f"Da ghi {out_png}")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    plot_spatial_density()
    plot_time_distribution()
