#!/usr/bin/env python3
"""
Request thu CDS: 1 bien, 1 thang, bbox Dong Nam A — de do thoi gian hang doi that truoc khi
quyet dinh chuyen han sang CDS thay ARCO-ERA5. KHONG anh huong gi den 3 tien trinh ARCO dang chay.

Chay: python3 scripts/test_cds_request.py
"""
import os
import time

import cdsapi

OUT = os.path.join(os.path.dirname(__file__), "..", "data_samples", "era5_cds_test", "2m_temperature_2020-01.nc")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

BBOX_AREA = [23, 92, -11, 141]  # North, West, South, East — khop BBOX trong download_era5_full.py


def main():
    t0 = time.time()
    print(f"Gui request luc {time.strftime('%H:%M:%S')} — dang cho hang doi CDS...")
    c = cdsapi.Client()
    c.retrieve(
        "reanalysis-era5-single-levels",
        {
            "product_type": "reanalysis",
            "variable": "2m_temperature",
            "year": "2020",
            "month": "01",
            "day": [f"{d:02d}" for d in range(1, 32)],
            "time": [f"{h:02d}:00" for h in range(24)],
            "area": BBOX_AREA,
            "data_format": "netcdf",
        },
        OUT,
    )
    dt = time.time() - t0
    size_mb = os.path.getsize(OUT) / 2**20
    print(f"\nXONG trong {dt:.0f}s ({dt/60:.1f} phut). File: {OUT} ({size_mb:.1f}MB)")


if __name__ == "__main__":
    main()
