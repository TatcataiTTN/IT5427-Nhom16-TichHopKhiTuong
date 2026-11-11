"""
Nen ban do thuc (coastline/border That tu Natural Earth qua cartopy) cho lop hieu ung
gio/may/mua ve tren canvas trong artifact. Anh tinh, khong phai du lieu dong -- chi dung
lam boi canh dia ly that cho cac diem/vector ve de len tren.

Chay: python3 viz/scripts/make_sea_basemap.py --out viz/output/sea_basemap.png
"""
import argparse

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

EXTENT = [92, 127, -11, 25]  # lon_min, lon_max, lat_min, lat_max
WIDTH_PX = 1400


def build(out_path: str) -> None:
    lon_span = EXTENT[1] - EXTENT[0]
    lat_span = EXTENT[3] - EXTENT[2]
    dpi = 150
    fig_w = WIDTH_PX / dpi
    fig_h = fig_w * (lat_span / lon_span)

    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.PlateCarree())
    ax.set_extent(EXTENT, crs=ccrs.PlateCarree())
    ax.set_aspect("auto")  # fill exactly [0,1]x[0,1] -- no cartopy auto-letterbox padding

    ax.set_facecolor("#0b1220")
    ax.add_feature(cfeature.OCEAN, facecolor="#0b1220")
    ax.add_feature(cfeature.LAND, facecolor="#17202b")
    ax.add_feature(cfeature.COASTLINE, edgecolor="#3a4a5c", linewidth=0.8)
    ax.add_feature(cfeature.BORDERS, edgecolor="#2e3b47", linewidth=0.6, linestyle=":")

    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.savefig(out_path, facecolor="#0b1220")
    plt.close(fig)
    w_px, h_px = round(fig_w * dpi), round(fig_h * dpi)
    print(f"Wrote {out_path} ({w_px}x{h_px}px)")
    print(f"extent used (for JS projection math, linear PlateCarree, fills image exactly 0..{w_px}x0..{h_px}): "
          f"lon {EXTENT[0]}..{EXTENT[1]}, lat {EXTENT[2]}..{EXTENT[3]} (lat axis inverted: y=0 is lat={EXTENT[3]})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="viz/output/sea_basemap.png")
    args = ap.parse_args()
    build(args.out)
