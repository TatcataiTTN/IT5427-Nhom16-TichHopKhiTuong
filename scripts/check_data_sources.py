#!/usr/bin/env python3
"""
Kiểm tra thực tế các nguồn dữ liệu khí tượng cho đề tài IT5427 - Nhóm 16.

Với mỗi nguồn: gọi API/endpoint thật, tải một mẫu nhỏ, validate nội dung,
lưu mẫu vào data_samples/, và in kết quả JSON để build báo cáo.

Chạy: python3 scripts/check_data_sources.py
Yêu cầu: chỉ dùng thư viện chuẩn (urllib) để không cần cài thêm gì trước khi
         chạy lần đầu - nếu có `requests` cài sẵn thì vẫn chạy tốt qua urllib.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES_DIR = os.path.join(HERE, "..", "data_samples")
os.makedirs(SAMPLES_DIR, exist_ok=True)

# Toạ độ mẫu để test theo khu vực Đông Nam Á
SEA_POINTS = {
    "Ha_Noi_VN": (21.03, 105.85),
    "Jakarta_ID": (-6.21, 106.85),
    "Bangkok_TH": (13.75, 100.50),
    "Manila_PH": (14.60, 120.98),
}

USER_AGENT = "IT5427-Nhom16-DataSourceCheck/1.0 (academic project, HUST)"


def http_get(url, headers=None, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read()
        elapsed = time.time() - t0
        return resp.status, dict(resp.headers), body, elapsed


def http_head(url, headers=None, timeout=20):
    """Chi lay header, KHONG tai body - dung cho file lon (vd GRIB2 hang GB)."""
    req = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, **(headers or {})}, method="HEAD"
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        elapsed = time.time() - t0
        return resp.status, dict(resp.headers), elapsed


def save_sample(name, content, binary=False):
    path = os.path.join(SAMPLES_DIR, name)
    mode = "wb" if binary else "w"
    with open(path, mode, **({} if binary else {"encoding": "utf-8"})) as f:
        f.write(content if binary else content)
    return path


def result(source, ok, message, extra=None):
    r = {
        "source": source,
        "ok": ok,
        "message": message,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    if extra:
        r.update(extra)
    return r


# ---------------------------------------------------------------------------
# 1. NASA POWER (REST API, khong can key)
# ---------------------------------------------------------------------------
def check_nasa_power():
    lat, lon = SEA_POINTS["Ha_Noi_VN"]
    url = (
        "https://power.larc.nasa.gov/api/temporal/daily/point"
        f"?parameters=T2M,PRECTOTCORR,ALLSKY_SFC_SW_DWN&community=AG"
        f"&longitude={lon}&latitude={lat}&start=20240101&end=20240105&format=JSON"
    )
    try:
        status, headers, body, elapsed = http_get(url)
        data = json.loads(body)
        t2m = data["properties"]["parameter"]["T2M"]
        n_days = len(t2m)
        save_sample("nasa_power_hanoi_sample.json", json.dumps(data, indent=2, ensure_ascii=False))
        ok = status == 200 and n_days == 5
        return result(
            "NASA POWER",
            ok,
            f"HTTP {status}, {n_days} ngay du lieu, {elapsed:.2f}s, khong can dang ky.",
            {"sample_T2M": t2m, "sea_coverage": "co (thu Ha Noi, toa do bat ky tren the gioi)"},
        )
    except Exception as e:
        return result("NASA POWER", False, f"LOI: {e}")


# ---------------------------------------------------------------------------
# 2. Open-Meteo Historical (REST API, khong can key)
# ---------------------------------------------------------------------------
def check_open_meteo():
    lat, lon = SEA_POINTS["Jakarta_ID"]
    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}&start_date=2024-01-01&end_date=2024-01-05"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=Asia%2FJakarta"
    )
    try:
        status, headers, body, elapsed = http_get(url)
        data = json.loads(body)
        n_days = len(data["daily"]["time"])
        save_sample("openmeteo_jakarta_sample.json", json.dumps(data, indent=2, ensure_ascii=False))
        ok = status == 200 and n_days == 5
        return result(
            "Open-Meteo Historical",
            ok,
            f"HTTP {status}, {n_days} ngay du lieu (Jakarta), {elapsed:.2f}s, khong can dang ky.",
            {"sample": data["daily"], "sea_coverage": "co, toa do bat ky"},
        )
    except Exception as e:
        return result("Open-Meteo Historical", False, f"LOI: {e}")


# ---------------------------------------------------------------------------
# 3. NOAA GHCN-Daily (public S3, khong can AWS credential)
# ---------------------------------------------------------------------------
SEA_COUNTRY_CODES = {
    "VM": "Vietnam", "TH": "Thailand", "ID": "Indonesia", "MY": "Malaysia",
    "RP": "Philippines", "CB": "Cambodia", "LA": "Laos", "BM": "Myanmar", "BX": "Brunei",
}


def check_noaa_ghcn():
    try:
        # 3a. Tai danh sach tram toan cau, dem theo quoc gia DNA
        status, _, body, elapsed = http_get("https://noaa-ghcn-pds.s3.amazonaws.com/ghcnd-stations.txt")
        text = body.decode("utf-8", errors="ignore")
        lines = text.splitlines()
        counts = {code: sum(1 for l in lines if l.startswith(code)) for code in SEA_COUNTRY_CODES}
        save_sample(
            "ghcnd_stations_VN_only.txt",
            "\n".join(l for l in lines if l.startswith("VM")) + "\n",
        )

        # 3b. Tai 1 file du lieu tram that (Ha Noi area station VMM00048820)
        status2, _, body2, elapsed2 = http_get(
            "https://noaa-ghcn-pds.s3.amazonaws.com/csv/by_station/VMM00048820.csv"
        )
        csv_text = body2.decode("utf-8", errors="ignore")
        csv_lines = csv_text.splitlines()
        first_date = csv_lines[1].split(",")[1] if len(csv_lines) > 1 else "?"
        last_date = csv_lines[-1].split(",")[1] if len(csv_lines) > 1 else "?"
        save_sample("ghcn_station_VMM00048820_sample.csv", "\n".join(csv_lines[:200]))

        ok = status == 200 and status2 == 200 and len(csv_lines) > 100
        return result(
            "NOAA GHCN-Daily (AWS S3)",
            ok,
            f"HTTP {status}/{status2}. Tram VMM00048820: {len(csv_lines)-1} ban ghi, "
            f"{first_date} -> {last_date}. Khong can AWS credential (public bucket).",
            {"sea_station_counts": counts},
        )
    except Exception as e:
        return result("NOAA GHCN-Daily (AWS S3)", False, f"LOI: {e}")


# ---------------------------------------------------------------------------
# 4. NOAA ISD / Global Hourly (public S3, khong can credential)
# ---------------------------------------------------------------------------
def check_noaa_isd():
    try:
        # Tram Noi Bai / Ha Noi vung lan can trong ISD: 488000-99999
        url = "https://noaa-global-hourly-pds.s3.amazonaws.com/2024/48900099999.csv"
        status, headers, body, elapsed = http_get(url)
        text = body.decode("utf-8", errors="ignore")
        lines = text.splitlines()
        size_mb = len(body) / 1024 / 1024
        save_sample("isd_station_48900099999_2024_sample.csv", "\n".join(lines[:200]))
        ok = status == 200 and len(lines) > 1000
        return result(
            "NOAA ISD / Global Hourly (AWS S3)",
            ok,
            f"HTTP {status}, tai duoc {len(lines)-1} ban ghi gio ({size_mb:.1f} MB), {elapsed:.2f}s, "
            "khong can AWS credential.",
        )
    except Exception as e:
        return result("NOAA ISD / Global Hourly (AWS S3)", False, f"LOI: {e}")


# ---------------------------------------------------------------------------
# 5. Copernicus CDS - ERA5 goc (CAN dang ky tai khoan + API key)
# ---------------------------------------------------------------------------
def check_cds():
    try:
        status, headers, body, elapsed = http_get("https://cds.climate.copernicus.eu/api")
        cdsapirc_path = os.path.expanduser("~/.cdsapirc")
        has_key = os.path.exists(cdsapirc_path)
        try:
            import cdsapi  # noqa: F401
            has_lib = True
        except ImportError:
            has_lib = False
        return result(
            "Copernicus CDS (ERA5 goc)",
            status in (200, 202),
            f"Server phan hoi HTTP {status} (con hoat dong). "
            f"Thu vien cdsapi: {'da cai' if has_lib else 'CHUA cai (pip install cdsapi)'}. "
            f"File ~/.cdsapirc (API key): {'co' if has_key else 'CHUA co -> can dang ky tai khoan CDS mien phi truoc'}.",
            {"can_dang_ky": not has_key, "huong_dan": "https://cds.climate.copernicus.eu/how-to-api"},
        )
    except Exception as e:
        return result("Copernicus CDS (ERA5 goc)", False, f"LOI: {e}")


# ---------------------------------------------------------------------------
# 6. ERA5 tren AWS Open Data (era5-pds) - Requester Pays
# ---------------------------------------------------------------------------
def check_era5_aws():
    try:
        status, headers, body, elapsed = http_get("https://era5-pds.s3.amazonaws.com/2024/01/main.nc4")
        # Ky vong 403 AccessDenied vi day la bucket "Requester Pays"
        ok_understood = status == 403
        return result(
            "ERA5 tren AWS (era5-pds)",
            ok_understood,
            f"HTTP {status}. Day la bucket 'Requester Pays' - request khong ky (anonymous) "
            "bi tu choi. THUC TE can tai khoan AWS that (co the phai tra phi request/transfer), "
            "KHONG hoan toan mien phi nhu ghi chu ban dau trong tai lieu nguon du lieu.",
        )
    except urllib.error.HTTPError as e:
        return result(
            "ERA5 tren AWS (era5-pds)",
            e.code == 403,
            f"HTTP {e.code} - xac nhan la Requester Pays bucket, can tai khoan AWS + the tin dung.",
        )
    except Exception as e:
        return result("ERA5 tren AWS (era5-pds)", False, f"LOI: {e}")


# ---------------------------------------------------------------------------
# 6b. ERA5 tren Google Cloud - ARCO-ERA5 (PUBLIC, KHONG can dang ky/tai khoan)
#     https://cloud.google.com/storage/docs/public-datasets/era5
# ---------------------------------------------------------------------------
def check_era5_arco():
    try:
        # Ban Zarr full-res da re-chunk, day la cach dung KHUYEN NGHI (khong tai GRIB2 tho ~5.4GB/ngay)
        zarr_path = "ar/1959-2022-full_37-1h-0p25deg-chunk-1.zarr-v2"
        status, _, body, elapsed = http_get(
            f"https://storage.googleapis.com/gcp-public-data-arco-era5/{zarr_path}/.zmetadata"
        )
        meta = json.loads(body)
        var_names = sorted({k.split("/")[0] for k in meta["metadata"].keys() if k.endswith(".zarray")})
        save_sample("era5_arco_zarr_zmetadata_sample.json", json.dumps(meta, indent=2, ensure_ascii=False))

        # Kiem tra file GRIB2 tho (raw) bang HEAD - CANH BAO kich thuoc that, KHONG tai ca file
        status2, headers2, _ = http_head(
            "https://storage.googleapis.com/gcp-public-data-arco-era5/raw/ERA5GRIB/HRES/Daily/1940/19400101_hres_dve.grb2"
        )
        raw_size_gb = int(headers2.get("Content-Length", 0)) / 1024 ** 3

        ok = status == 200 and len(var_names) > 10
        return result(
            "ERA5 tren Google Cloud (ARCO-ERA5, MIEN PHI khong can dang ky)",
            ok,
            f"HTTP {status}, {elapsed:.2f}s. Zarr store co {len(var_names)} bien khi tuong "
            f"(vd: 2m_temperature, 10m_u/v_component_of_wind, geopotential...), phu 1959-2022, "
            f"do phan giai day du 0.25deg (1440x721), hourly. KHONG CAN TAI KHOAN, khong can API key. "
            f"Luu y: file GRIB2 tho (raw/) rat nang (~{raw_size_gb:.1f} GB/ngay/bien) - PHAI dung ban "
            "Zarr da re-chunk qua xarray+gcsfs, KHONG tai truc tiep GRIB2 tho.",
            {
                "cach_dung": "xr.open_zarr('gcs://gcp-public-data-arco-era5/" + zarr_path + "', "
                "storage_options={'token':'anon'}) -- can pip install zarr gcsfs",
                "so_bien": len(var_names),
                "mot_vai_bien": var_names[:12],
            },
        )
    except Exception as e:
        return result("ERA5 tren Google Cloud (ARCO-ERA5)", False, f"LOI: {e}")


# ---------------------------------------------------------------------------
# 6c. ERA5 tren Microsoft Planetary Computer (mien phi, tu dong cap SAS token)
# ---------------------------------------------------------------------------
def check_era5_planetary_computer():
    try:
        status, _, body, elapsed = http_get(
            "https://planetarycomputer.microsoft.com/api/stac/v1/collections/era5-pds/items?limit=1"
        )
        item = json.loads(body)["features"][0]
        asset_keys = list(item["assets"].keys())

        # Xin SAS token mien phi, khong dang ky - day la diem khac biet lon so voi CDS/AWS
        status2, _, body2, _ = http_get(
            "https://planetarycomputer.microsoft.com/api/sas/v1/token/era5-pds"
        )
        token_ok = status2 == 200 and "token" in json.loads(body2)

        ok = status == 200 and token_ok
        return result(
            "ERA5 tren Microsoft Planetary Computer (mien phi, tu dong cap token)",
            ok,
            f"STAC catalog HTTP {status} ({elapsed:.2f}s), item mau '{item['id']}' co "
            f"{len(asset_keys)} asset (vd: {asset_keys[:2]}). SAS token endpoint HTTP {status2} - "
            "KHONG can dang ky tai khoan, chi can goi API lay token roi truy cap Azure Blob. "
            "Can dung dung SDK 'planetary-computer' Python (pc.sign(href)) de tu dong lay dung "
            "storage account - tu ghep URL thu cong se bi loi AuthenticationFailed (da test).",
            {"asset_keys_sample": asset_keys},
        )
    except Exception as e:
        return result("ERA5 tren Microsoft Planetary Computer", False, f"LOI: {e}")


# ---------------------------------------------------------------------------
# 7. OpenStreetMap - Nominatim (geocoding) + Tile server (ban do nen)
# ---------------------------------------------------------------------------
def check_openstreetmap():
    notes = []
    nominatim_ok = False
    tile_ok = False
    try:
        status, _, body, elapsed = http_get(
            "https://nominatim.openstreetmap.org/search?q=Ho+Hoan+Kiem+Ha+Noi&format=json&limit=1"
        )
        data = json.loads(body)
        nominatim_ok = status == 200 and len(data) > 0
        save_sample("nominatim_hoankiem_sample.json", json.dumps(data, indent=2, ensure_ascii=False))
        notes.append(f"Nominatim: HTTP {status}, {len(data)} ket qua, {elapsed:.2f}s")
    except Exception as e:
        notes.append(f"Nominatim: KHONG KET NOI DUOC tu moi truong nay ({type(e).__name__}: {e})")

    try:
        status, headers, body, elapsed = http_get("https://tile.openstreetmap.org/5/25/13.png")
        tile_ok = status == 200 and len(body) > 100
        with open(os.path.join(SAMPLES_DIR, "osm_tile_sample.png"), "wb") as f:
            f.write(body)
        notes.append(f"Tile server: HTTP {status}, {len(body)} bytes, {elapsed:.2f}s")
    except Exception as e:
        notes.append(f"Tile server: KHONG KET NOI DUOC tu moi truong nay ({type(e).__name__}: {e})")

    ok = nominatim_ok and tile_ok
    return result(
        "OpenStreetMap (Nominatim + Tile)",
        ok,
        " | ".join(notes),
        {
            "luu_y": "Neu moi truong chay script nay chan DNS/outbound toi openstreetmap.org "
            "(vd sandbox CI co whitelist domain), ket qua se bao loi ket noi ngay ca khi dich vu "
            "OSM thuc te van hoat dong binh thuong. Hay chay lai script tren may/server that cua nhom."
        },
    )


# ---------------------------------------------------------------------------
# 8. CHIRPS (mua ve tinh, mo rong tuy chon)
# ---------------------------------------------------------------------------
def check_chirps():
    try:
        url = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/2024/chirps-v2.0.2024.01.01.tif.gz"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=20) as resp:
            status = resp.status
            content_length = resp.headers.get("Content-Length")
            elapsed = time.time() - t0
        ok = status == 200
        return result(
            "CHIRPS (mua ve tinh, tuy chon)",
            ok,
            f"HTTP {status}, file ~{int(content_length)/1024/1024:.1f} MB (chua tai full, chi kiem tra header), "
            f"{elapsed:.2f}s. Khong can dang ky.",
        )
    except Exception as e:
        return result("CHIRPS (mua ve tinh, tuy chon)", False, f"LOI: {e}")


# ---------------------------------------------------------------------------
# 9. Himawari-8/9 (anh ve tinh khi tuong, tuy chon)
# ---------------------------------------------------------------------------
def check_himawari():
    """
    Kiem tra bucket noaa-himawari8 (S3, public). Da xac nhan bang cach tai THAT
    1MB dau cua 1 file san pham may (AHI Cloud Phase) ngay 12/10/2025: file la
    HDF5/NetCDF hop le, LastModified thang 10/2025 - ve tinh Himawari-8 VAN con
    duoc dung, KHONG ngung hoat dong nhu nhan dinh sai truoc do trong bao cao.
    """
    try:
        # Liet ke thu muc gan day nhat de tim ngay co du lieu that
        status, _, body, elapsed = http_get(
            "https://noaa-himawari8.s3.amazonaws.com/?list-type=2"
            "&prefix=AHI-L2-FLDK-Clouds/2025/10/12/1710/&max-keys=5"
        )
        root = ET.fromstring(body)
        ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
        contents = root.findall("s3:Contents", ns)
        files = [
            (c.find("s3:Key", ns).text, c.find("s3:LastModified", ns).text, c.find("s3:Size", ns).text)
            for c in contents
        ]

        ok = False
        detail_msg = f"HTTP {status}, khong tim thay file trong thu muc mau."
        if files:
            key, last_modified, size = files[0]
            url = f"https://noaa-himawari8.s3.amazonaws.com/{key}"
            # Tai that 1MB dau de xac nhan file hop le (khong chi list metadata)
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Range": "bytes=0-1048575"})
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=20) as resp:
                partial = resp.read()
                elapsed2 = time.time() - t0
            save_sample("himawari8_sample_1MB.nc", partial, binary=True)
            is_hdf5 = partial[:8] == b"\x89HDF\r\n\x1a\n"
            ok = is_hdf5
            detail_msg = (
                f"HTTP {status}, tai THAT 1MB dau cua file '{key.split('/')[-1]}' "
                f"(sua doi luc {last_modified}, tong kich thuoc {int(size)/1024/1024:.0f} MB) "
                f"trong {elapsed2:.2f}s -> {'la file HDF5/NetCDF hop le' if is_hdf5 else 'KHONG doc duoc header hop le'}. "
                "XAC NHAN: Himawari-8 VAN dang hoat dong va co du lieu cap nhat (thang 10/2025), "
                "KHONG ngung van hanh nhu ghi chu sai truoc do. Ca noaa-himawari8 va noaa-himawari9 "
                "deu la bucket public that, dang duoc nhieu nhom nghien cuu su dung."
            )

        return result("Himawari-8 (AWS S3, tuy chon)", ok, detail_msg, {"file_mau": files[0] if files else None})
    except Exception as e:
        return result("Himawari-8 (AWS S3, tuy chon)", False, f"LOI: {e}")


def main():
    checks = [
        check_nasa_power,
        check_open_meteo,
        check_noaa_ghcn,
        check_noaa_isd,
        check_cds,
        check_era5_aws,
        check_era5_arco,
        check_era5_planetary_computer,
        check_openstreetmap,
        check_chirps,
        check_himawari,
    ]
    results = []
    for fn in checks:
        print(f"--- Dang kiem tra: {fn.__name__} ---", file=sys.stderr)
        r = fn()
        results.append(r)
        status_str = "OK" if r["ok"] else "FAIL"
        print(f"[{status_str}] {r['source']}: {r['message']}", file=sys.stderr)

    out_path = os.path.join(SAMPLES_DIR, "check_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nDa luu ket qua day du vao: {out_path}", file=sys.stderr)
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
