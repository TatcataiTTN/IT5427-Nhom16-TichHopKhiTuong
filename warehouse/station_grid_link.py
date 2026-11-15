"""
Lien ket (link) tram/diem voi o luoi ERA5 thay vi gop (merge): tram la mot DIEM do, o luoi ERA5 la
trung binh cua mot o 0,25 do (~28 km) tren dia hinh mo hinh. Hai thuc the khac nhau cung quan trac
mot hien tuong, nen ta ghi lai QUAN HE giua chung (bang lien ket) va giu nguyen ca hai chuoi, khong
hop nhat thanh mot ban ghi.

Bang lien ket: location_id -> tam o ERA5 gan nhat, khoang cach toi tam o, do cao dia hinh mo hinh
ERA5 tai o do va tai dung vi tri tram (noi suy Bilinear, giong cach kho WeatherObs noi suy ERA5),
do cao tram, do lech do cao. Kho chua tai truong dia the vi (geopotential 'z') cua ERA5, nen do cao
dia hinh mo hinh duoc UOC LUONG tu chinh ERA5 bang phuong trinh thuy tinh (hypsometric):
    h = (Rd / g) * Tm * ln(MSL / SP),   Tm = T2m + 0,0065 * h / 2   (lap toi hoi tu)
tren trung binh 12 thang nam 2020 cua SP, MSL, T2m.

Kiem tra: o bien khoi phai cho h ~ 0; do lech do cao phai giai thich duoc mot phan bias nhiet do
tram - ERA5 (bias_monthly.parquet) theo gradient giam nhiet do theo do cao.

Chay: python3 warehouse/station_grid_link.py
Output: warehouse/output/station_grid_link.parquet, station_grid_link_summary.json
"""
import json
import os

import numpy as np
import pandas as pd
import xarray as xr

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(os.path.dirname(__file__), "output")
ERA5 = os.path.join(ROOT, "data_samples", "era5_full")
RD, G, LAPSE = 287.05, 9.80665, 0.0065
GRID = 0.25


def mean_field(var, short, months):
    acc = None
    for m in months:
        with xr.open_dataset(os.path.join(ERA5, var, f"{m}.nc")) as ds:
            f = ds[short].mean("time").load()
        acc = f if acc is None else acc + f
    return acc / len(months)


def model_height():
    months = [f"2020-{k:02d}" for k in range(1, 13)]
    sp = mean_field("surface_pressure", "surface_pressure", months)
    msl = mean_field("mean_sea_level_pressure", "mean_sea_level_pressure", months)
    t2 = mean_field("2m_temperature", "2m_temperature", months)
    h = xr.zeros_like(sp)
    for _ in range(10):
        h = (RD / G) * (t2 + LAPSE * h / 2) * np.log(msl / sp)
    return h  # m, toa do latitude giam dan, longitude tang dan


def bilinear(h, lat, lon):
    return float(h.interp(latitude=lat, longitude=lon, method="linear"))


def haversine_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371.0088 * np.arcsin(np.sqrt(a))


def main():
    h = model_height()
    ocean = {"Bien Dong 15N 115E": (15.0, 115.0), "Thai Binh Duong 10N 135E": (10.0, 135.0),
             "Bien Java 5S 110E": (-5.0, 110.0), "An Do Duong 5S 95E": (-5.0, 95.0)}
    ocean_h = {k: round(float(h.sel(latitude=la, longitude=lo)), 1) for k, (la, lo) in ocean.items()}
    print("Kiem tra o bien khoi (ky vong ~0 m):", ocean_h)

    loc = pd.read_parquet(os.path.join(OUT, "location.parquet"))
    rows = []
    for r in loc.itertuples():
        clat = round(r.lat / GRID) * GRID
        clon = round(r.lon / GRID) * GRID
        rows.append({
            "location_id": r.location_id, "type": r.type, "country": r.country, "lat": r.lat, "lon": r.lon,
            "era5_cell_lat": clat, "era5_cell_lon": clon,
            "dist_to_cell_centre_km": round(float(haversine_km(r.lat, r.lon, clat, clon)), 2),
            "era5_height_cell_m": round(float(h.sel(latitude=clat, longitude=clon)), 1),
            "era5_height_bilinear_m": round(bilinear(h, r.lat, r.lon), 1),
            "station_elev_m": r.elevation_m,
            "relation": "quan_trac_cung_hien_tuong",   # lien ket, khong phai "cung thuc the"
        })
    link = pd.DataFrame(rows)
    link["elev_offset_m"] = (link["station_elev_m"] - link["era5_height_bilinear_m"]).round(1)

    b = pd.read_parquet(os.path.join(OUT, "bias_monthly.parquet"))
    tb = b[b["var"] == "temp_mean"].groupby("location_id").apply(
        lambda d: np.average(d["bias"], weights=d["n_days"]), include_groups=False).rename("temp_bias_mean_c")
    link = link.merge(tb, on="location_id", how="left")
    link.to_parquet(os.path.join(OUT, "station_grid_link.parquet"), index=False)

    v = link.dropna(subset=["temp_bias_mean_c", "elev_offset_m"])
    slope, icpt = np.polyfit(v["elev_offset_m"] / 1000, v["temp_bias_mean_c"], 1)
    r = float(np.corrcoef(v["elev_offset_m"], v["temp_bias_mean_c"])[0, 1])
    corrected = v["temp_bias_mean_c"] + LAPSE * 1000 * v["elev_offset_m"] / 1000
    big = link.reindex(link["elev_offset_m"].abs().sort_values(ascending=False).index).head(5)
    summary = {
        "so_vi_tri": int(len(link)),
        "kiem_tra_o_bien": ocean_h,
        "dist_to_cell_centre_km": {"median": float(link["dist_to_cell_centre_km"].median()),
                                   "max": float(link["dist_to_cell_centre_km"].max())},
        "elev_offset_m": {"median": float(link["elev_offset_m"].median()),
                          "median_abs": float(link["elev_offset_m"].abs().median()),
                          "min": float(link["elev_offset_m"].min()), "max": float(link["elev_offset_m"].max()),
                          "so_vi_tri_abs_gt_100m": int((link["elev_offset_m"].abs() > 100).sum())},
        "lech_lon_nhat": big[["location_id", "country", "station_elev_m", "era5_height_bilinear_m",
                              "elev_offset_m", "temp_bias_mean_c"]].round(2).astype(str).to_dict("records"),
        "hoi_quy_bias_nhiet_theo_do_lech_do_cao": {
            "so_tram": int(len(v)), "do_doc_C_per_km": round(float(slope), 2), "chan": round(float(icpt), 2),
            "r": round(r, 2), "gradient_chuan_C_per_km": -LAPSE * 1000,
            "bias_tb_truoc_hieu_chinh": round(float(v["temp_bias_mean_c"].mean()), 2),
            "bias_tb_abs_truoc": round(float(v["temp_bias_mean_c"].abs().mean()), 2),
            "bias_tb_abs_sau_hieu_chinh_6_5": round(float(corrected.abs().mean()), 2),
        },
    }
    with open(os.path.join(OUT, "station_grid_link_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
    plot_figure(link, slope, icpt, r)


def vn(x, d=1):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def plot_figure(link, slope, icpt, r):
    """Hinh 2 o: (a) phan bo trong so Fellegi-Sunter + nguong; (b) do lech do cao vs bias nhiet."""
    import sys
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.expanduser("~/.claude/skills/visualization-report-maps/scripts"))
    import report_style as rs
    rs.set_textwidth(441.02)
    rs.apply()

    p = pd.read_parquet(os.path.join(OUT, "er_fellegi_sunter_pairs.parquet"))
    with open(os.path.join(OUT, "er_fellegi_sunter_summary.json"), encoding="utf-8") as f:
        s = json.load(f)
    th_h, th_l = s["theta_h"], s["theta_l"]

    fig, (a, b) = plt.subplots(1, 2, figsize=(rs.TW, 2.95), dpi=300)
    bins = np.linspace(p["weight"].min() - 0.5, p["weight"].max() + 0.5, 40)
    groups = [("Khớp (nhãn WMO)", p["label_meta"] == 1, "#1b8a5a"),
              ("Không khớp (nhãn WMO)", p["label_meta"] == 0, "#9e9e9e"),
              ("Chưa có nhãn", p["label_meta"].isna(), "#e3a33b")]
    a.hist([p.loc[m, "weight"] for _, m, _ in groups], bins=bins, stacked=True,
           color=[c for *_, c in groups], label=[l for l, *_ in groups], edgecolor="white", linewidth=0.3)
    a.set_yscale("log")
    for t, txt in ((th_h, f"θh = {vn(th_h, 2)}"), (th_l, f"θl = {vn(th_l, 2)}")):
        a.axvline(t, color="#333", linestyle="--", linewidth=0.8)
        a.text(t + 0.3, 0.98, txt, fontsize=6.5, rotation=90, va="top", ha="left",
               transform=a.get_xaxis_transform())
    a.set_xlabel(r"Trọng số Fellegi–Sunter $w=\sum\log_2(m/u)$", fontsize=8)
    a.set_ylabel("Số cặp (thang log)", fontsize=8)
    a.legend(fontsize=5.8, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.3), ncol=3,
             handlelength=1.0, columnspacing=0.8)
    a.set_title("(a) 2.262 cặp ứng viên GHCN × ISD", fontsize=8.5, fontweight="bold")

    v = link.dropna(subset=["temp_bias_mean_c"])
    b.scatter(v["elev_offset_m"], v["temp_bias_mean_c"], s=12, color="#0072B2", edgecolor="white",
              linewidth=0.4, zorder=3)
    xs = np.linspace(v["elev_offset_m"].min() - 20, v["elev_offset_m"].max() + 20, 50)
    b.plot(xs, icpt + slope * xs / 1000, color="#c0392b", linewidth=1,
           label=f"Hồi quy: {vn(slope, 2)} °C/km, r = {vn(r, 2)}")
    b.plot(xs, -LAPSE * xs, color="#333", linestyle=":", linewidth=1, label="Gradient chuẩn −6,5 °C/km")
    lp = v.loc[v["elev_offset_m"].idxmin()]
    b.annotate("Luang Prabang (ISD)", (lp["elev_offset_m"], lp["temp_bias_mean_c"]), fontsize=6.3,
               xytext=(8, -4), textcoords="offset points")
    b.axhline(0, color="#bbb", linewidth=0.6)
    b.axvline(0, color="#bbb", linewidth=0.6)
    b.set_xlabel("Độ cao trạm − độ cao địa hình ERA5 (m)", fontsize=8)
    b.set_ylabel("Bias nhiệt TB: trạm − ERA5 (°C)", fontsize=8)
    b.legend(fontsize=5.8, frameon=False, loc="lower left")
    b.set_title(f"(b) {len(v)} trạm có chuỗi bias nhiệt độ", fontsize=8.5, fontweight="bold")
    for ax in (a, b):
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(labelsize=7)
    fig.tight_layout()
    out_png = os.path.join(ROOT, "report", "figures", "er_fs_station_grid.png")
    rs.save(fig, out_png)
    print("Da ghi", out_png)


if __name__ == "__main__":
    main()
