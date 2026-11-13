"""
Kiem tra ca 9 loai bien ERA5 da tai (qua CDS hoac ARCO, cung mot dinh dang dau ra
data_samples/era5_full/<bien>/<YYYY-MM>.nc) dung cau truc, dung bbox, khong NaN toan phan, va gia
tri nam trong khoang vat ly hop ly — khong chi kiem tay 1 file nhu luc dau (2m_temperature 2020-01),
ma kiem tu dong CA 9 LOAI, chay lai duoc bat ky luc nao trong qua trinh tai.

Chay:  pytest tests/test_era5_full.py -v
       pytest tests/test_era5_full.py -v -m "not slow"   # bo qua test doi het 540 file
"""
import glob
import os
import sys

import numpy as np
import pytest
import xarray as xr

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.download_era5_cds import VARIABLES, CDS_SHORTNAME  # noqa: E402
from scripts.download_era5_full import BBOX  # noqa: E402

ERA5_DIR = os.path.join(os.path.dirname(__file__), "..", "data_samples", "era5_full")

# Khoang vat ly hop ly de bat loi tho (don vi SAU khi warehouse/interpolation.py quy doi,
# nhung file .nc goc o day van don vi ERA5 goc: K, Pa, m, 0-1...) — chi dung don vi GOC cua
# tung bien nhu CDS/ARCO tra ve, chua qua buoc quy doi trong interpolation.py.
RAW_RANGES = {
    "2m_temperature": (200.0, 330.0),               # Kelvin, ~-73..57C du rong cho ca Dong Nam A
    # Mua/buc xa: ERA5 (GRIB nen) co the cho gia tri am cuc nho gan 0 do nhieu so khi nen/giai nen
    # (dac tinh da biet cua ECMWF, khong phai loi vat ly that) -- cho ngoc gan 0 thay vi ep dung 0.0.
    "total_precipitation": (-0.001, 0.5),            # m/gio, 500mm/gio la qua ro rang du
    "10m_u_component_of_wind": (-60.0, 60.0),        # m/s
    "10m_v_component_of_wind": (-60.0, 60.0),
    "surface_pressure": (50000.0, 110000.0),         # Pa
    "mean_sea_level_pressure": (85000.0, 110000.0),  # Pa
    "toa_incident_solar_radiation": (-10.0, 20_000_000.0),       # J/m^2 tich luy 1 gio
    "total_cloud_cover": (0.0, 1.0),                 # ty le 0-1
    "surface_solar_radiation_downwards": (-10.0, 20_000_000.0),  # J/m^2
}


def _files_for(var):
    return sorted(glob.glob(os.path.join(ERA5_DIR, var, "*.nc")))


def _any_file_per_variable():
    """1 file dai dien cho moi bien, de parametrize — rong neu bien do chua co file nao."""
    out = []
    for var in VARIABLES:
        files = _files_for(var)
        if files:
            out.append((var, files[0]))
    return out


REPRESENTATIVE = _any_file_per_variable()


@pytest.mark.skipif(not REPRESENTATIVE, reason="chua co file ERA5 nao duoc tai")
@pytest.mark.parametrize("var,fp", REPRESENTATIVE, ids=[v for v, _ in REPRESENTATIVE])
def test_variable_has_correct_name_and_dims(var, fp):
    """Moi file phai co dung 1 data variable ten = var (sau khi CDS doi tu ten ngan nhu t2m),
    voi 3 chieu time/latitude/longitude — dung dinh dang warehouse/interpolation.py can."""
    ds = xr.open_dataset(fp)
    assert var in ds.data_vars, f"{fp}: thieu bien '{var}', co {list(ds.data_vars)}"
    da = ds[var]
    assert set(da.dims) == {"time", "latitude", "longitude"}, f"{fp}: dims sai {da.dims}"
    assert "expver" not in ds.coords, f"{fp}: con sot coord 'expver' cua CDS, chua duoc don"
    ds.close()


@pytest.mark.skipif(not REPRESENTATIVE, reason="chua co file ERA5 nao duoc tai")
@pytest.mark.parametrize("var,fp", REPRESENTATIVE, ids=[v for v, _ in REPRESENTATIVE])
def test_variable_covers_exact_bbox(var, fp):
    """Luoi phai dung khop BBOX trong scripts/download_era5_full.py (ca ARCO lan CDS phai cat
    dung cung 1 vung, neu khong 2 nguon se khong ghep duoc)."""
    ds = xr.open_dataset(fp)
    lat, lon = ds.latitude.values, ds.longitude.values
    assert lat.max() == pytest.approx(BBOX["lat_max"], abs=0.26)
    assert lat.min() == pytest.approx(BBOX["lat_min"], abs=0.26)
    assert lon.max() == pytest.approx(BBOX["lon_max"], abs=0.31)
    assert lon.min() == pytest.approx(BBOX["lon_min"], abs=0.26)
    ds.close()


@pytest.mark.skipif(not REPRESENTATIVE, reason="chua co file ERA5 nao duoc tai")
@pytest.mark.parametrize("var,fp", REPRESENTATIVE, ids=[v for v, _ in REPRESENTATIVE])
def test_variable_not_all_nan_and_in_physical_range(var, fp):
    """Khong toan NaN (tai hong/cat sai vung), va gia tri nam trong khoang vat ly cho phep
    (bat loi tho nhu don vi sai, chua quy doi, hoac file bi hong giua chung)."""
    ds = xr.open_dataset(fp)
    values = ds[var].values
    assert not np.isnan(values).all(), f"{fp}: toan NaN"
    finite = values[np.isfinite(values)]
    assert finite.size > 0, f"{fp}: khong co gia tri huu han nao"
    lo, hi = RAW_RANGES[var]
    frac_out = float(((finite < lo) | (finite > hi)).mean())
    assert frac_out < 0.001, (
        f"{fp}: {frac_out:.4%} gia tri ngoai khoang vat ly [{lo},{hi}] -- "
        f"min={finite.min():.3g}, max={finite.max():.3g}")
    ds.close()


@pytest.mark.skipif(not REPRESENTATIVE, reason="chua co file ERA5 nao duoc tai")
@pytest.mark.parametrize("var,fp", REPRESENTATIVE, ids=[v for v, _ in REPRESENTATIVE])
def test_month_has_expected_hour_count(var, fp):
    """So gio trong file phai khop dung so gio cua thang (vd thang 31 ngay = 744 gio) — bat
    truong hop CDS/ARCO tra ve thieu gio giua chung ma khong bao loi."""
    import pandas as pd
    month = os.path.splitext(os.path.basename(fp))[0]  # "YYYY-MM"
    ds = xr.open_dataset(fp)
    first = pd.Timestamp(f"{month}-01")
    last = first + pd.offsets.MonthEnd(0) + pd.Timedelta(hours=23)
    expected = int((last - first) / pd.Timedelta(hours=1)) + 1
    assert ds.sizes["time"] == expected, f"{fp}: {ds.sizes['time']}/{expected} gio"
    ds.close()


def test_no_leftover_part_files():
    """Khong con file .part do (nghia la khong co lan ghi nao bi ngat giua chung ma khong don
    dep — dam bao atomic write that su hoat dong dung)."""
    leftover = glob.glob(os.path.join(ERA5_DIR, "*", "*.part"))
    assert leftover == [], f"con {len(leftover)} file .part chua don: {leftover[:5]}"


def test_no_duplicate_or_corrupt_zero_byte_files():
    for var in VARIABLES:
        for fp in _files_for(var):
            assert os.path.getsize(fp) > 1_000_000, f"{fp}: chi {os.path.getsize(fp)} byte, qua nho/co the hong"


@pytest.mark.slow
def test_all_540_files_present_and_distinct_months():
    """Test day du: chi PASS khi ca 540 file (9 bien x 60 thang) da tai xong. Dung de xac nhan
    hoan tat cuoi cung, khong phai de chay trong luc dang tai do (se FAIL, dung y)."""
    for var in VARIABLES:
        files = _files_for(var)
        months = {os.path.splitext(os.path.basename(f))[0] for f in files}
        assert len(files) == 60, f"{var}: {len(files)}/60 thang"
        assert len(months) == 60, f"{var}: co thang bi trung/thieu, chi {len(months)} thang duy nhat"


if __name__ == "__main__":
    done = sum(len(_files_for(v)) for v in VARIABLES)
    print(f"Tien do hien tai: {done}/540 file ERA5 — chay 'pytest tests/test_era5_full.py -v -m \"not slow\"' "
          f"de kiem tra phan da co ngay bay gio.")
