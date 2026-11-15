"""
Ve dung tung DIEM di thuong khi hau (khong gop thanh mat do):
  anomaly_event_maps.png        2 ban do: z nhiet do 30/4/2024 (nang nong) va z ap suat 7/9/2024 (bao Yagi)
  anomaly_station_timeseries.png 2 chuoi ngay tai tram: Bangkok 1-7/2024 (nhiet do), Hai Phong 8-10/2024
                                 (ap suat), co khi hau nen, dai +-2 sigma, diem bat thuong/cuc doan.
So lieu doc truc tiep tu warehouse/output/anomaly_daily.parquet va location.parquet.

Chay: python3 warehouse/plot_anomaly_points.py
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.expanduser("~/.claude/skills/visualization-report-maps/scripts"))
import report_style as rs
import map_helpers as mh
import fetch_boundaries as fb

OUT = os.path.join(os.path.dirname(__file__), "..", "report", "figures")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
ASEAN = ["VNM", "THA", "IDN", "MYS", "PHL", "LAO", "MMR", "KHM", "BRN", "SGP", "TLS"]
STATION_SRC = ["GHCN", "ISD"]
C_BT, C_CD = "#eda100", "#c0392b"


def vn(x, dec=1):
    return f"{x:.{dec}f}".replace(".", ",").replace("-", "−")


def load():
    a = pd.read_parquet(os.path.join(OUTPUT_DIR, "anomaly_daily.parquet"),
                        columns=["location_id", "source", "date", "var", "value", "clim_mean",
                                 "clim_std", "z", "flag"])
    a["date"] = pd.to_datetime(a["date"])
    loc = pd.read_parquet(os.path.join(OUTPUT_DIR, "location.parquet"))
    return a, loc


def basemap(ax, world, ext):
    lat0 = (ext[2] + ext[3]) / 2
    ax.set_aspect(mh.aspect_for_lat(lat0))
    world[world["ISO_A3"].isin(ASEAN)].plot(ax=ax, facecolor="#f1f2ee", edgecolor="#8a9479",
                                            linewidth=0.5, zorder=1)
    world[(world["CONTINENT"] == "Asia") & ~world["ISO_A3"].isin(ASEAN)].plot(
        ax=ax, facecolor="#f6f5f0", edgecolor="#ccc", linewidth=0.3, zorder=0)
    ax.set_xlim(ext[0], ext[1])
    ax.set_ylim(ext[2], ext[3])
    return lat0


def scatter_z(ax, d, vmax):
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
    d = d.sort_values("z", key=np.abs)  # diem |z| lon ve sau cung, khong bi che
    sc = None
    for is_station, marker in [(False, "s"), (True, "o")]:
        sub = d[d["source"].isin(STATION_SRC) == is_station]
        az = sub["z"].abs()
        size = np.where(az >= 2, 46 if is_station else 26, 18 if is_station else 9)
        edge = np.where(az >= 3, "black", "white")
        lw = np.where(az >= 3, 0.9, 0.3)
        sc = ax.scatter(sub["lon"], sub["lat"], c=sub["z"], cmap="RdBu_r", norm=norm, s=size,
                        marker=marker, edgecolors=edge, linewidths=lw, zorder=4 if is_station else 3)
    return sc


def plot_event_maps(a, loc):
    rs.set_textwidth(441.02)
    rs.apply()
    world = fb.natural_earth("admin_0_countries", scale="10m",
                             cache_dir=os.path.join(os.path.dirname(__file__), "boundaries"))
    d1 = a[(a["date"] == "2024-04-30") & (a["var"] == "temp_mean")].merge(loc, on="location_id")
    d2 = a[(a["date"] == "2024-09-07") & (a["var"] == "pmsl_min")].merge(loc, on="location_id")
    print(f"30/4/2024 temp: {len(d1)} dong, {d1['location_id'].nunique()} vi tri, "
          f"|z|>=2: {(d1['z'].abs() >= 2).sum()}, |z|>=3: {(d1['z'].abs() >= 3).sum()}")
    print(f"7/9/2024 pmsl: {len(d2)} dong, {d2['location_id'].nunique()} vi tri, "
          f"z<=-2: {(d2['z'] <= -2).sum()}, z<=-3: {(d2['z'] <= -3).sum()}")

    fig, axs = plt.subplots(1, 2, figsize=(rs.TW, rs.TW * 0.62), constrained_layout=True,
                            gridspec_kw={"width_ratios": [1.25, 1]})
    # (a) toan ASEAN
    ext_a = (91, 128, -11, 26)
    lat0 = basemap(axs[0], world, ext_a)
    sc = scatter_z(axs[0], d1, 4)
    top = d1.loc[d1["z"].idxmax()]
    axs[0].annotate(f"{top['location_id']} ({top['source']})\n{vn(top['value'])}°C, z = +{vn(top['z'], 2)}",
                    xy=(top["lon"], top["lat"]), xytext=(111.0, 21.0),
                    fontsize=6.0, ha="left", arrowprops=dict(arrowstyle="-", linewidth=0.6),
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#999", lw=0.4), zorder=6)
    mh.lonlat_axes(axs[0], dec=0, n=4)
    rs.north_arrow(axs[0], x=0.92, y=0.88, color="black")
    rs.scalebar_deg(axs[0], lat0, color="black", loc=(0.05, 0.05))
    cb = fig.colorbar(sc, ax=axs[0], location="bottom", shrink=0.8, pad=0.02, aspect=30)
    cb.set_label("z nhiệt độ trung bình ngày", fontsize=7)
    cb.ax.tick_params(labelsize=6.5)
    axs[0].set_title("(a) Nắng nóng, 30/4/2024", fontsize=8.5, fontweight="bold")

    # (b) phong to lục dia va Bac Bo, noi bao Yagi do bo
    ext_b = (97, 112, 8, 24)
    lat0b = basemap(axs[1], world, ext_b)
    sc2 = scatter_z(axs[1], d2[d2["lon"].between(ext_b[0], ext_b[1]) & d2["lat"].between(ext_b[2], ext_b[3])], 7)
    hp = d2[(d2["location_id"] == "48825199999") & (d2["source"] == "ERA5")].iloc[0]
    axs[1].annotate(f"Hải Phòng (48825199999, ERA5)\n{vn(hp['value'])} hPa, z = {vn(hp['z'], 1)}",
                    xy=(hp["lon"], hp["lat"]), xytext=(107.4, 17.2),
                    fontsize=6.0, ha="left", arrowprops=dict(arrowstyle="-", linewidth=0.6),
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#999", lw=0.4), zorder=6)
    mh.lonlat_axes(axs[1], dec=0, n=4)
    rs.scalebar_deg(axs[1], lat0b, color="black", loc=(0.05, 0.05))
    cb2 = fig.colorbar(sc2, ax=axs[1], location="bottom", shrink=0.8, pad=0.02, aspect=30)
    cb2.set_label("z áp suất mực nước biển thấp nhất ngày", fontsize=7)
    cb2.ax.tick_params(labelsize=6.5)
    axs[1].set_title("(b) Bão Yagi, 7/9/2024", fontsize=8.5, fontweight="bold")

    handles = [Line2D([], [], marker="o", ls="", mfc="#bbb", mec="white", ms=6, label="Trạm (GHCN/ISD)"),
               Line2D([], [], marker="s", ls="", mfc="#bbb", mec="white", ms=4, label="Lưới (ERA5/NASA/Open-Meteo)"),
               Line2D([], [], marker="o", ls="", mfc="white", mec="black", mew=0.9, ms=6, label="|z| ≥ 3 (cực đoan)")]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=6.5, frameon=False,
               bbox_to_anchor=(0.5, -0.045))
    out = os.path.join(OUT, "anomaly_event_maps.png")
    rs.save(fig, out)
    print(f"Da ghi {out} | max 30/4: {top['location_id']} {top['source']} {top['value']:.2f} z={top['z']:.2f}")


def series_panel(ax, s, unit, title):
    s = s.sort_values("date")
    lo, hi = s["clim_mean"] - 2 * s["clim_std"], s["clim_mean"] + 2 * s["clim_std"]
    ax.fill_between(s["date"], lo, hi, color="#9ecae1", alpha=0.35, linewidth=0, label="Nền ± 2σ")
    ax.plot(s["date"], s["clim_mean"], color="#2171b5", linewidth=1.0, label="Khí hậu nền (±15 ngày)")
    ax.plot(s["date"], s["value"], color="#555", linewidth=0.6, marker="o", ms=1.6, label="Giá trị ngày")
    bt, cd = s[s["flag"] == "bat_thuong"], s[s["flag"] == "cuc_doan"]
    ax.scatter(bt["date"], bt["value"], s=22, color=C_BT, edgecolor="black", linewidth=0.4, zorder=5,
               label=f"Bất thường |z| ≥ 2 ({len(bt)} ngày)")
    ax.scatter(cd["date"], cd["value"], s=30, color=C_CD, edgecolor="black", linewidth=0.5, zorder=6,
               label=f"Cực đoan |z| ≥ 3 ({len(cd)} ngày)")
    ax.set_ylabel(unit, fontsize=7.5)
    ax.set_title(title, fontsize=8.3, fontweight="bold", loc="left")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
    ax.tick_params(labelsize=6.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle=":", linewidth=0.5, alpha=0.6)
    return bt, cd


def plot_station_series(a):
    rs.set_textwidth(441.02)
    rs.apply()
    bkk = a[(a["location_id"] == "TH000048455") & (a["source"] == "GHCN") & (a["var"] == "temp_mean")
            & a["date"].between("2024-01-01", "2024-07-31")]
    hp = a[(a["location_id"] == "48825199999") & (a["source"] == "ERA5") & (a["var"] == "pmsl_min")
           & a["date"].between("2024-08-01", "2024-10-31")]
    fig, axs = plt.subplots(2, 1, figsize=(rs.TW, 3.75), constrained_layout=True)
    bt, cd = series_panel(axs[0], bkk, "°C", "(a) Bangkok TH000048455 (GHCN), nhiệt độ trung bình ngày, 1–7/2024")
    axs[0].legend(loc="lower center", fontsize=6.0, ncol=3, frameon=False)
    mn = bkk.loc[bkk["z"].idxmax()]
    axs[0].annotate(f"{mn['date']:%d/%m}: {vn(mn['value'])}°C, z = +{vn(mn['z'], 2)}",
                    xy=(mn["date"], mn["value"]), xytext=(mn["date"] + pd.Timedelta(days=22), mn["value"] + 0.4),
                    fontsize=6.3, arrowprops=dict(arrowstyle="-", linewidth=0.6))
    ylo, yhi = axs[0].get_ylim()
    axs[0].set_ylim(ylo - 2.5, yhi + 0.6)
    print(f"Bangkok: {len(bkk)} ngay, bat_thuong {len(bt)}, cuc_doan {len(cd)}, max z {mn['z']:.2f} ngay {mn['date']:%Y-%m-%d}")

    bt2, cd2 = series_panel(axs[1], hp, "hPa", "(b) Hải Phòng 48825199999 (ERA5 nội suy), áp suất mực nước biển thấp nhất ngày, 8–10/2024")
    m2 = hp.loc[hp["z"].idxmin()]
    axs[1].annotate(f"Bão Yagi {m2['date']:%d/%m}: {vn(m2['value'])} hPa, z = {vn(m2['z'], 1)}",
                    xy=(m2["date"], m2["value"]), xytext=(m2["date"] + pd.Timedelta(days=9), m2["value"] + 1.5),
                    fontsize=6.3, arrowprops=dict(arrowstyle="-", linewidth=0.6))
    axs[1].legend(loc="upper left", fontsize=6.0, ncol=3, frameon=False)
    y2lo, y2hi = axs[1].get_ylim()
    axs[1].set_ylim(y2lo, y2hi + 5)
    print(f"Hai Phong: {len(hp)} ngay, bat_thuong {len(bt2)}, cuc_doan {len(cd2)}, min {m2['value']:.1f} z {m2['z']:.2f} ngay {m2['date']:%Y-%m-%d}")
    out = os.path.join(OUT, "anomaly_station_timeseries.png")
    rs.save(fig, out)
    print(f"Da ghi {out}")


if __name__ == "__main__":
    a, loc = load()
    plot_event_maps(a, loc)
    plot_station_series(a)
