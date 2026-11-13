"""
Ban do khu vuc nghien cuu — dung skill visualization-report-maps (report_style + map_helpers,
Natural Earth admin_0 that cho ranh gioi 11 nuoc ASEAN — Timor-Leste gia nhap 26/10/2025), ve
dung 119 vi tri that trong warehouse/location.py, phan theo nguon du lieu. Kiem tra truc quan:
co phu het ASEAN khong? (cau tra loi that: KHONG — Singapore va Timor-Leste khong co tram nao,
xem ghi chu duoi hinh).

Chay: python3 warehouse/plot_study_area_map.py
"""
import os
import sys

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from shapely.geometry import box

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.expanduser("~/.claude/skills/visualization-report-maps/scripts"))
import report_style as rs
import map_helpers as mh
import fetch_boundaries as fb
from warehouse.location import build_location_table

OUT_PNG = os.path.join(os.path.dirname(__file__), "..", "report", "figures", "study_area_map.png")
BBOX = {"lat_min": -11, "lat_max": 23, "lon_min": 92, "lon_max": 141}

ASEAN_ISO3 = {
    "VNM": "Vietnam", "THA": "Thailand", "IDN": "Indonesia", "MYS": "Malaysia",
    "PHL": "Philippines", "LAO": "Laos", "MMR": "Myanmar", "KHM": "Cambodia",
    "BRN": "Brunei", "SGP": "Singapore", "TLS": "Timor-Leste",
}
NO_DATA_ISO3 = {"SGP", "TLS"}  # ASEAN nhung nhom khong co tram/diem nao
SRC_COLOR = {"GHCN": "#2a78d6", "ISD": "#eb6834", "NASA_POWER/Open-Meteo": "#1baf7a"}


def classify_source(location_id: str) -> str:
    """Suy nguon tu dang location_id that (quy uoc da dung trong warehouse/location.py):
    chu thuong co dinh (hanoi, hcmc, jakarta...) = 6 diem NASA_POWER/Open-Meteo;
    11 chu so lien tiep (USAF+WBAN) = ISD; con lai (ma chu+so kieu VMM000...) = GHCN."""
    if location_id.islower():
        return "NASA_POWER/Open-Meteo"
    if location_id.isdigit() and len(location_id) == 11:
        return "ISD"
    return "GHCN"


def main():
    rs.set_textwidth(441.02)
    rs.apply()

    print("Dang tai ranh gioi quoc gia that (Natural Earth admin_0, co cache)...")
    world = fb.natural_earth("admin_0_countries", scale="10m", cache_dir=os.path.join(os.path.dirname(__file__), "boundaries"))
    print(f"  {len(world)} quoc gia trong lop nen, nam du lieu Natural Earth 10m")
    asean = world[world["ISO_A3"].isin(ASEAN_ISO3.keys())].copy()
    asean["co_du_lieu"] = ~asean["ISO_A3"].isin(NO_DATA_ISO3)
    print(f"  Loc ra {len(asean)}/11 nuoc ASEAN; thieu: "
          f"{[v for k,v in ASEAN_ISO3.items() if k not in asean['ISO_A3'].values] or 'khong thieu nuoc nao trong lop nen'}")

    loc = build_location_table()
    loc["nguon"] = loc["location_id"].map(classify_source)
    print(f"  {len(loc)} vi tri that, {loc['country'].nunique()} nuoc co du lieu")
    covered_countries = set(loc["country"].unique())
    missing = [v for v in ASEAN_ISO3.values() if v not in covered_countries]
    print(f"  Nuoc ASEAN KHONG co tram nao: {missing}")

    fig, ax = plt.subplots(figsize=(rs.TW, rs.TW * 0.86))
    lat0 = (BBOX["lat_min"] + BBOX["lat_max"]) / 2
    ax.set_aspect(mh.aspect_for_lat(lat0))

    # Nen: tat ca nuoc ASEAN, to mau khac nhau ro co/khong co du lieu
    asean[asean["co_du_lieu"]].plot(ax=ax, facecolor="#dce8d5", edgecolor="#5a6b4f", linewidth=0.6, zorder=1)
    asean[~asean["co_du_lieu"]].plot(ax=ax, facecolor="#f6d4d4", edgecolor="#9a3b3b", linewidth=0.9,
                                     hatch="///", zorder=1)
    # Cac nuoc lan can ngoai ASEAN (ngu canh) de nguoi xem dinh vi duoc, mau trung tinh
    others = world[(world["CONTINENT"] == "Asia") & (~world["ISO_A3"].isin(ASEAN_ISO3.keys()))]
    others.plot(ax=ax, facecolor="#eee9df", edgecolor="#bbb", linewidth=0.4, zorder=0)

    # Khung bbox nghien cuu that
    bbox_poly = gpd.GeoSeries([box(BBOX["lon_min"], BBOX["lat_min"], BBOX["lon_max"], BBOX["lat_max"])], crs=4326)
    bbox_poly.boundary.plot(ax=ax, color="#9a3b3b", linewidth=1.3, linestyle=(0, (5, 3)), zorder=3)

    # 119 vi tri that, mau theo nguon
    for src, color in SRC_COLOR.items():
        sub = loc[loc["nguon"] == src]
        ax.scatter(sub["lon"], sub["lat"], s=16 if src != "NASA_POWER/Open-Meteo" else 42,
                  marker="o" if src != "NASA_POWER/Open-Meteo" else "^",
                  c=color, edgecolor="white", linewidth=0.4, zorder=4, label=f"{src} ({len(sub)})")

    # Nhan ten nuoc ASEAN (tru Singapore/Timor-Leste, qua nho hoac can nhan rieng -- tach ra co duong dan)
    for iso3, name in ASEAN_ISO3.items():
        if iso3 in NO_DATA_ISO3:
            continue
        row = world[world["ISO_A3"] == iso3]
        if row.empty:
            continue
        c = row.geometry.representative_point().iloc[0]
        if not (BBOX["lon_min"] - 8 <= c.x <= BBOX["lon_max"] + 8 and BBOX["lat_min"] - 8 <= c.y <= BBOX["lat_max"] + 8):
            continue
        ax.annotate(name, (c.x, c.y), zorder=5, fontsize=6.5, ha="center", color="#2b2b2b")

    # Singapore: toa do that (~103.8E, 1.35N), nhan tach ra vung trong phia duoi, co duong dan
    sg_lon, sg_lat = 103.82, 1.35
    ax.annotate("Singapore — KHÔNG có trạm nào", xy=(sg_lon, sg_lat), xytext=(109.5, -4.5),
               fontsize=6.3, ha="left", va="center", color="#9a3b3b", fontweight="bold", zorder=6,
               arrowprops=dict(arrowstyle="-", color="#9a3b3b", linewidth=0.8,
                               shrinkA=2, shrinkB=2))

    # Timor-Leste: toa do that (~125.6E, -8.8S), nhan tach rieng, co duong dan (gia nhap ASEAN 26/10/2025)
    tl_lon, tl_lat = 125.6, -8.8
    ax.annotate("Timor-Leste — KHÔNG có trạm nào", xy=(tl_lon, tl_lat), xytext=(131.0, -6.0),
               fontsize=6.3, ha="left", va="center", color="#9a3b3b", fontweight="bold", zorder=6,
               arrowprops=dict(arrowstyle="-", color="#9a3b3b", linewidth=0.8,
                               shrinkA=2, shrinkB=2))

    ax.set_xlim(BBOX["lon_min"] - 6, BBOX["lon_max"] + 6)
    ax.set_ylim(BBOX["lat_min"] - 6, BBOX["lat_max"] + 6)
    mh.lonlat_axes(ax, dec=0, n=5)
    rs.north_arrow(ax, x=0.08, y=0.92, color="black")
    rs.scalebar_deg(ax, lat0, color="black", loc=(0.06, 0.04))

    handles, labels = ax.get_legend_handles_labels()
    missing_patch = mpatches.Patch(facecolor="#f6d4d4", edgecolor="#9a3b3b", hatch="///",
                                   label="ASEAN, chưa có trạm (Singapore, Timor-Leste)")
    ax.legend(handles=handles + [missing_patch], loc="lower right", fontsize=6.2, frameon=True,
             framealpha=0.9, edgecolor="#ccc")
    ax.set_title("Khu vực nghiên cứu: bbox thật dùng để tải ERA5 + 119 vị trí trạm/điểm",
                 fontsize=9.5, fontweight="bold")

    os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
    rs.save(fig, OUT_PNG)
    print(f"Da ghi {OUT_PNG}")
    print(f"\nKET LUAN: {len(covered_countries)}/11 nuoc ASEAN co du lieu thuc te. "
         f"Thieu: {missing}. Vung bbox tai ERA5 (lat {BBOX['lat_min']}..{BBOX['lat_max']}, "
         f"lon {BBOX['lon_min']}..{BBOX['lon_max']}) co bao trum lanh tho Singapore ve mat dia ly "
         f"(Singapore nam trong bbox), nhung KHONG co tram quan trac diem nao duoc nhom chon tai.")


if __name__ == "__main__":
    main()
