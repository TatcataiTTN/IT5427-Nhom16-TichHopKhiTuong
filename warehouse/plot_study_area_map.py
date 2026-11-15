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
# Vi tri nhan ten nuoc (lon, lat, can le), chon tay de nam o vung trong, khong de len diem tram
COUNTRY_LABEL_POS = {
    "Myanmar": (97.3, 25.6, "center"), "Laos": (102.1, 21.5, "center"),
    "Vietnam": (110.3, 16.6, "left"), "Thailand": (101.4, 15.7, "center"),
    "Cambodia": (104.9, 13.1, "center"), "Malaysia": (104.6, 4.8, "left"),
    "Brunei": (113.9, 6.0, "right"), "Indonesia": (113.4, -1.2, "center"),
    "Philippines": (126.4, 13.6, "left"),
}
NO_DATA_MARKERS = {"1": (103.82, 1.35), "2": (125.9, -8.75)}


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

    # Nhan ten nuoc dat tay vao vung trong (bien hoac dat lien khong co diem), khong de chu de len diem
    # tram; ha="left"/"right" chon theo phia con trong.
    for name, (x, y, ha) in COUNTRY_LABEL_POS.items():
        ax.text(x, y, name, fontsize=6.5, ha=ha, va="center", color="#2b2b2b", zorder=5,
                style="italic")

    # Singapore (~103,82°E; 1,35°N) va Timor-Leste (~125,6°E; -8,8°N): danh dau so ①② dat ngay tai
    # cho, giai thich trong chu giai -- khong dung duong dan dai cat ngang ban do.
    for num, (x, y) in NO_DATA_MARKERS.items():
        ax.scatter([x], [y], s=70, facecolor="white", edgecolor="#9a3b3b", linewidth=1.1, zorder=7)
        ax.text(x, y, num, fontsize=6.3, ha="center", va="center", color="#9a3b3b",
                fontweight="bold", zorder=8)

    ax.set_xlim(BBOX["lon_min"] - 6, BBOX["lon_max"] + 6)
    ax.set_ylim(BBOX["lat_min"] - 6, BBOX["lat_max"] + 6)
    mh.lonlat_axes(ax, dec=0, n=5)
    # Mui ten Bac dat o vinh Bengal (ngoai bbox, bien trong), khong de len goc khung bbox
    rs.north_arrow(ax, x=0.045, y=0.80, color="black", size=0.06)
    rs.scalebar_deg(ax, lat0, color="black", loc=(0.04, 0.04))

    handles, labels = ax.get_legend_handles_labels()
    missing_patch = mpatches.Patch(facecolor="#f6d4d4", edgecolor="#9a3b3b", hatch="///",
                                   label="Nước ASEAN chưa có trạm: (1) Singapore, (2) Timor-Leste")
    bbox_handle = plt.Line2D([], [], color="#9a3b3b", linewidth=1.3, linestyle=(0, (5, 3)),
                             label="Khung bbox tải ERA5")
    # Chu giai dat duoi ban do, ngoai vung du lieu
    ax.legend(handles=handles + [bbox_handle, missing_patch], loc="upper center",
              bbox_to_anchor=(0.5, -0.07), ncol=2, fontsize=6.4, frameon=False,
              columnspacing=1.2, handletextpad=0.5)
    ax.set_title("Khu vực nghiên cứu: khung tải ERA5 và 119 vị trí trạm/điểm",
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
