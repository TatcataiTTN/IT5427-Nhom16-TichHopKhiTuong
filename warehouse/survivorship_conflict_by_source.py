"""
Tinh lai ty le xung dot Survivorship THEO SO NGUON THAT, sua loi phuong phap trong lan do dau:
ham resolve_survivorship() goc (warehouse/survivorship.py) gom tat ca BAN GHI (khong gop theo nguon)
trong 1 ngay roi so sanh min/max -- neu 1 nguon tan suat gio (vd ISD) co nhieu gio trong ngay, bien
thien tu nhien trong ngay (vd nhiet do sang-trua) bi tinh nham thanh "xung dot giua cac nguon".

Script nay gop truoc ve 1 gia tri trung binh / nguon / ngay, roi moi so sanh giua CAC NGUON KHAC
NHAU -- dung dinh nghia "xung dot giua nguon" ma Survivorship can do luong. Dong thoi bao cao ro
so nhom (vi tri, ngay) THUC SU co >=2 nguon de so sanh, vi mot bien chi co 1 nguon (hoac cac nguon
khong bao gio trung vi tri+ngay) thi ty le xung dot 0% la VO NGHIA, khong phai bang chung dong y.

Chay: python3 warehouse/survivorship_conflict_by_source.py
"""
import os

import duckdb

WAREHOUSE = os.path.join(os.path.dirname(__file__), "output", "weatherobs.parquet")

THRESHOLDS = {
    "temp_c": 10.0,
    "rh_pct": 20.0,
    "precip_mm": 50.0,
    "wind_speed_ms": 30.0,
    "pressure_surface_hpa": 2.0,
    "pressure_msl_hpa": 2.0,
}
PRIORITY = {"ISD": 1, "GHCN": 1, "ERA5": 2, "OPEN_METEO": 3, "NASA_POWER": 4}


def main():
    for col, thr in THRESHOLDS.items():
        q = f"""
        SELECT location_id, date_trunc('day', timestamp_utc) AS d, source, avg({col}) AS v
        FROM read_parquet('{WAREHOUSE}/**/*.parquet', hive_partitioning=1)
        WHERE {col} IS NOT NULL
        GROUP BY location_id, d, source
        """
        df = duckdb.sql(q).df()
        df["prio"] = df["source"].map(PRIORITY).fillna(99)

        n_sources_overall = sorted(df["source"].unique().tolist())
        conflicts, multi = 0, 0
        for (_loc, _d), g in df.groupby(["location_id", "d"]):
            if g["source"].nunique() < 2:
                continue
            multi += 1
            winner = g.sort_values("prio").iloc[0]
            spread_pct = (g["v"].max() - g["v"].min()) / (abs(winner["v"]) + 1e-6) * 100.0
            if spread_pct > thr:
                conflicts += 1

        if multi == 0:
            print(f"{col}: nguon co du lieu = {n_sources_overall} -- KHONG co nhom (vi tri,ngay) nao "
                  f"co >=2 nguon trung nhau. Ty le xung dot 0% la VO NGHIA (khong the xung dot).")
        else:
            print(f"{col}: nguon = {n_sources_overall} | nhom co >=2 nguon that: {multi} | "
                  f"xung dot that: {conflicts} ({100 * conflicts / multi:.1f}%)")


if __name__ == "__main__":
    main()
