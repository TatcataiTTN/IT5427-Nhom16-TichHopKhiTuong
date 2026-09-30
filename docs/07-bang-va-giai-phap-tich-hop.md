# Bảng ánh xạ trường dữ liệu tổng hợp & Giải pháp tích hợp chi tiết

Tiếp nối `06-truong-du-lieu-va-tich-hop.md`. File này là tài liệu **thi công được** — TV2 (Schema Lead) và TV1 (Ingestion Lead) dùng trực tiếp bảng dưới để viết code, không cần suy luận lại từ đầu.

---

## 1. Bảng ánh xạ tổng hợp — 1 hàng = 1 trường Mediated Schema, nhìn ngang thấy ngay nguồn nào có/thiếu/cần xử lý gì

Ký hiệu: ✅ = có sẵn dùng ngay · 🔧 = có nhưng cần biến đổi (unit/parse/derive) · ✗ = không có ở nguồn này

| Trường Mediated Schema | NASA POWER | Open-Meteo | GHCN-Daily | NOAA ISD | ERA5 (ARCO) | Số nguồn trùng | Loại xử lý chính |
|---|---|---|---|---|---|---|---|
| `temp_c` | ✅ `T2M` | ✅ `temperature_2m` | 🔧 `TAVG/TMAX/TMIN` (PIVOT, /10 °C) | 🔧 `TMP` (PARSE, /10 °C) | ✅ `2m_temperature` (K→°C) | **5/5** | **Survivorship** (mục 3) |
| `rh_pct` | ✅ `RH2M` | ✅ `relative_humidity_2m` | ✗ | ✗ (chỉ có DEW) | ✗ (chỉ có specific_humidity) | 2/5 trực tiếp | **Derive vật lý** (mục 4a) cho 2 nguồn còn lại |
| `dewpoint_c` | ✅ `T2MDEW` | ✗ (derivable từ T+RH) | ✗ | 🔧 `DEW` (PARSE, /10 °C) | ✗ (derivable từ specific_humidity+T+P) | 2/5 trực tiếp | Derive vật lý cho phần thiếu, không bắt buộc |
| `precip_mm` | ✅ `PRECTOTCORR` | ✅ `precipitation` | 🔧 `PRCP` (PIVOT, /10 mm) | ⚠️ không có field số riêng (chỉ có trong `REM`/METAR gốc nếu có nhóm giáng thủy) | ✅ `total_precipitation` (m→mm) | 4/5 | **Survivorship + missing-value policy đặc biệt** (mục 3, mưa) |
| `wind_speed_ms` | ✅ `WS10M` (vô hướng có sẵn) | ✅ `wind_speed_10m` | ✗ | 🔧 `WND` (PARSE, sub-field tốc độ) | 🔧 derive từ `10m_u/v_component_of_wind`: $\sqrt{u^2+v^2}$ | 4/5 (sau derive) | Chuẩn hoá biểu diễn (mục 4b) |
| `wind_dir_deg` | ✗ (POWER không trả hướng) | ✅ `wind_direction_10m` | ✗ | 🔧 `WND` (PARSE, sub-field hướng) | 🔧 derive: $\text{atan2}(-u,-v)$ | 3/5 (sau derive) | Chuẩn hoá biểu diễn |
| `pressure_surface_hpa` | 🔧 `PS` (kPa→hPa, ×10) | ✗ | ✗ | ✗ | ✅ `surface_pressure` (Pa→hPa, /100) | 2/5 | Giữ **tách riêng** khỏi `pressure_msl` (mục 3 — lỗi nghiêm trọng nếu gộp) |
| `pressure_msl_hpa` | ✗ | ✅ `pressure_msl` | ✗ | 🔧 `SLP` (PARSE, /10 hPa) | ✅ `mean_sea_level_pressure` (Pa→hPa) | 3/5 | Survivorship trong nhóm MSL, **không** so với `pressure_surface_hpa` |
| `solar_rad_wm2` | 🔧 `ALLSKY_SFC_SW_DWN` (MJ/m²/ngày → W/m², xem mục 4c) | ✅ `shortwave_radiation` (đã W/m²) | ✗ | ✗ | ⚠️ `toa_incident_solar_radiation` — **đây là bức xạ đỉnh khí quyển (TOA), KHÔNG phải bức xạ bề mặt** — không so trực tiếp với 2 cột kia | 2/5 thật sự tương đương | Cảnh báo Semantic Heterogeneity (mục 4c) |
| `cloud_cover_pct` | ✗ | ✅ `cloud_cover` | ✗ | 🔧 `GA1`–`GA4` (PARSE, đơn vị oktas 0–8 → ×12.5 = %) | ✅ `total_cloud_cover` (0–1 → ×100) | 3/5 | Unit conversion đơn giản, ít rủi ro |
| `soil_temp_c`, `soil_moist_m3m3` | ✗ | ✅ | ✗ | ✗ | ✗ (không có trong 35 biến ARCO đã kiểm chứng — bản ERA5 đầy đủ trên CDS có nhưng cần xác nhận lại) | 1/5 | Không có overlap → **ingest thẳng**, không cần tích hợp |
| `visibility_m` | ✗ | ✗ | ✗ | 🔧 `VIS` (PARSE) | ✗ | 1/5 | Không có overlap → ingest thẳng |
| `elevation_m` (thuộc `Location`, không phải `WeatherObs`) | ✗ (API không trả) | ✅ (trả kèm response) | ✅ (metadata trạm `ghcnd-stations.txt`) | ✅ `ELEVATION` | 🔧 derive từ `geopotential_at_surface / 9.80665` | metadata, không phải time-series | Dùng làm **khoá quy đổi** `pressure_surface ↔ pressure_msl` (mục 4d) |

**Đọc nhanh bảng này:** cột "Số nguồn trùng" cao (temp_c: 5/5, precip_mm: 4/5) → cần **Giải pháp Survivorship**. Dòng có `✗` nhiều (soil_temp, visibility) → không có gì để tích hợp, chỉ cần ingest. Dòng có ký hiệu ⚠️ (solar_rad, pressure) → **rủi ro tích hợp sai nếu không đọc kỹ đơn vị/định nghĩa vật lý**.

---

## 2. 7 giải pháp tích hợp cụ thể — mỗi giải pháp gắn với 1 nhóm vấn đề trong bảng trên

### Giải pháp 1 — GAV Union đơn giản (áp dụng: `rh_pct`, `precip_mm` phần POWER/Open-Meteo, `cloud_cover`, `soil_temp/moist`)

Không có xung đột thật sự, chỉ cần map tên cột + đổi đơn vị. Code mẫu (PySpark):

```python
df_power_std = df_power.select(
    col("loc_id"), col("date"),
    lit("NASA_POWER").alias("source"),
    col("T2M").alias("temp_c"),
    col("RH2M").alias("rh_pct"),
    col("PRECTOTCORR").alias("precip_mm"),
    (col("PS") * 10).alias("pressure_surface_hpa"),   # kPa -> hPa
)
```

### Giải pháp 2 — PIVOT (áp dụng: toàn bộ GHCN-Daily)

GHCN ở dạng "long" (1 dòng/biến/ngày) — bắt buộc pivot trước khi UNION với 4 nguồn "wide" còn lại:

```python
df_ghcn_wide = (
    df_ghcn.groupBy("ID", "DATE")
    .pivot("ELEMENT", ["TMAX", "TMIN", "TAVG", "PRCP"])
    .agg(first("DATA_VALUE"))
    .withColumn("temp_c", col("TAVG") / 10.0)        # GHCN luu don vi x10
    .withColumn("precip_mm", col("PRCP") / 10.0)
)
```

### Giải pháp 3 — PARSE trường nén (áp dụng: toàn bộ NOAA ISD)

Mỗi trường ISD là 1 chuỗi CSV lồng bên trong ô CSV ngoài — cần regex/split 2 tầng:

```python
from pyspark.sql.functions import split, col

# TMP format: "+0250,1"  -> gia tri x10 do C, flag chat luong
df_isd = df_isd.withColumn("tmp_parts", split(col("TMP"), ","))
df_isd = df_isd.withColumn("temp_c", (col("tmp_parts")[0].cast("int") / 10.0))
df_isd = df_isd.withColumn("temp_qc", col("tmp_parts")[1])
df_isd = df_isd.filter(col("temp_qc").isin(["1", "5"]))   # chi giu flag "passed QC"

# WND format: "999,9,V,0005,1" -> huong,qc,type,tocdo(x10 m/s),qc
df_isd = df_isd.withColumn("wnd_parts", split(col("WND"), ","))
df_isd = df_isd.withColumn("wind_dir_deg", col("wnd_parts")[0].cast("int"))
df_isd = df_isd.withColumn("wind_speed_ms", col("wnd_parts")[3].cast("int") / 10.0)
```

> Giá trị `999`/`9999`/`99999` trong ISD là **mã thiếu dữ liệu** (missing code) — bắt buộc convert thành NULL trước khi tính toán, giống hệt xử lý `-9999` đã ghi trong `03-ke-hoach-160-tasks.md` (Tuần 2, TV1 #6).

### Giải pháp 4 — Survivorship Rule cho trường bị trùng thật sự (áp dụng: `temp_c`, `precip_mm`, `pressure_msl_hpa`)

Đây là phần áp dụng trực tiếp khái niệm **Survivorship** trong `1. Introduction.pdf` (slide 46, pipeline Schema Alignment → Entity Resolution → **Data Fusion**) và tinh thần Fellegi-Sunter (match/non-match/possible-match) của `3_RecordLinkage_ER.pdf`.

**Bước 1 — Xếp hạng độ tin cậy nguồn** (áp dụng ý tưởng "Sources Profiling" — buổi 5 sắp tới trong lịch học):

| Hạng | Nguồn | Lý do |
|---|---|---|
| 1 (cao nhất) | ISD/GHCN (trạm) | Đo trực tiếp tại điểm, có QC flag |
| 2 | ERA5 | Đồng hoá số liệu quan trắc + mô hình vật lý, độ phân giải cao nhất trong nhóm mô hình |
| 3 | Open-Meteo | Nội suy từ ERA5 — về bản chất "phái sinh" từ hạng 2 |
| 4 (thấp nhất) | NASA POWER | Vệ tinh/MERRA-2, độ phân giải thô nhất (0.5°/1°) |

**Bước 2 — Hàm quyết định (pseudocode), giống cấu trúc `match/possible-match/non-match` trong slide:**

```python
def survivorship_temp(station_val, era5_val, openmeteo_val, power_val, threshold=3.0):
    """
    threshold: nguong lech (°C) coi la 'possible-match' can canh bao,
               tương tự nguong t trong slide Similarity Measures (s(x,y) >= t)
    """
    if station_val is not None:
        primary = station_val
        source = "STATION"
    elif era5_val is not None:
        primary = era5_val
        source = "ERA5"
    elif openmeteo_val is not None:
        primary = openmeteo_val
        source = "OPEN_METEO"
    else:
        primary = power_val
        source = "NASA_POWER"

    # Veracity check: neu co ca station VA mo hinh, do lech qua lon -> gan co "possible conflict"
    flag = None
    if station_val is not None and era5_val is not None:
        diff = abs(station_val - era5_val)
        if diff > threshold:
            flag = f"CONFLICT: station-ERA5 lech {diff:.1f}C"

    return primary, source, flag
```

**Với mưa (`precip_mm`)**, KHÔNG dùng cùng 1 hàm trên vì mưa không "mượt" như nhiệt độ — áp dụng chính sách đã ghi trong đề xuất đề tài (mục 5.2): khi trạm thiếu, **không lấy trung bình 3 nguồn còn lại** (sẽ làm loãng tín hiệu mưa cực đoan) mà giữ **max** của các nguồn mô hình làm cận trên cảnh báo, đồng thời gắn cờ `low_confidence=True` để Dashboard hiển thị khác màu.

### Giải pháp 5 — Derive vật lý (áp dụng: `rh_pct` cho ISD/ERA5, `elevation_m` cho ERA5)

```python
import math

def relative_humidity_from_dewpoint(temp_c, dewpoint_c):
    """Cong thuc Clausius-Clapeyron - dung nguyen tu de xuat de tai muc 5.3"""
    def es(t):  # ap suat hoi bao hoa
        return 611.2 * math.exp((17.67 * t) / (t + 243.5))
    e = es(dewpoint_c)
    e_s = es(temp_c)
    return round((e / e_s) * 100, 1)

def elevation_from_geopotential(geopotential_at_surface):
    """g = 9.80665 m/s^2 (chuan WMO)"""
    return geopotential_at_surface / 9.80665
```

Dùng hàm `relative_humidity_from_dewpoint` cho ISD (đã có `temp_c`, `dewpoint_c` sau PARSE) — **không** cần chạy PINN đầy đủ cho bước này, công thức đóng đã đủ chính xác; PINN chỉ cần thiết nếu muốn *đồng thời* làm mượt nhiều biến nhiễu chéo nhau (xem `06-truong-du-lieu-va-tich-hop.md` mục 4b để biết ranh giới rõ khi nào mới cần PINN thật).

### Giải pháp 6 — Cảnh báo & tách bạch Semantic Heterogeneity (áp dụng: `solar_rad_wm2`, `pressure_*_hpa`)

Đây không phải bug cần "sửa" mà là **rủi ro tích hợp sai cần chặn ở tầng schema**:

- Đặt **CHECK constraint** hoặc unit test khi ETL: `pressure_surface_hpa` phải nằm trong khoảng hợp lý theo cao độ trạm (dùng công thức khí áp chuẩn ước lượng, nếu lệch > 50 hPa so với ước lượng → cảnh báo lỗi map nhầm cột).
- **Không đưa `toa_incident_solar_radiation` (ERA5) vào cùng cột với `shortwave_radiation`/`ALLSKY_SFC_SW_DWN`** — nếu đề tài cần bức xạ bề mặt từ ERA5, phải lấy đúng biến `surface_solar_radiation_downwards` (cần xác nhận biến này có trong bản CDS đầy đủ hay không — bản ARCO 35-biến đã kiểm tra **không có**, chỉ có biến TOA). Đây là việc TV1 cần làm khi đăng ký CDS xong: kiểm tra lại danh mục biến đầy đủ, khác với 35 biến rút gọn của ARCO.

### Giải pháp 7 — Spatial Interpolation trước, PINN sau (áp dụng: ghép ERA5 lưới với trạm điểm)

Theo đúng thứ tự đã có trong đề xuất đề tài — **không nhảy thẳng vào PINN**:

1. **Bước rẻ trước**: Bilinear Interpolation 4 ô lưới ERA5 quanh mỗi trạm → có ngay giá trị "ERA5 tại điểm trạm" để dùng cho Giải pháp 4 (Survivorship).
2. **Bước nâng cao nếu còn thời gian**: Kriging (tính đến hiệp phương sai không gian, tốt hơn ở địa hình phức tạp ven biển/núi ĐNA).
3. **Chỉ dùng PINN khi** cần tạo **trường liên tục mới** tốt hơn cả lưới gốc ERA5 (VD: bản đồ gió mịn 1km cho dashboard) — đây là hạng mục **tuỳ chọn, điểm cộng**, không nằm trên đường găng (critical path) của tiến độ.

---

## 3. Checklist áp dụng cho TV2 (thứ tự triển khai đề xuất)

1. Viết 5 connector chuẩn hoá (Giải pháp 1–3) cho từng nguồn → output đúng schema `WeatherObs` ở `06-truong-du-lieu-va-tich-hop.md` mục 2.
2. Chạy Bilinear Interpolation (Giải pháp 7, bước 1) để có "ERA5 tại điểm trạm" trước khi làm Survivorship.
3. Cài hàm Survivorship (Giải pháp 4) cho `temp_c`, `precip_mm`, `pressure_msl_hpa` — output thêm 2 cột `source_used` và `conflict_flag` để phục vụ Data Quality Report.
4. Cài hàm derive vật lý (Giải pháp 5) cho `rh_pct` ở ISD/ERA5.
5. Viết unit test cảnh báo (Giải pháp 6) cho `pressure_surface_hpa` và `solar_rad_wm2` trước khi merge.
6. Bilinear (đã làm ở bước 2) là đủ cho tiến độ chính; Kriging/PINN (Giải pháp 7 bước 2–3) chỉ làm nếu Tuần 3 còn dư thời gian, đúng như risk mitigation đã ghi trong đề xuất đề tài.
