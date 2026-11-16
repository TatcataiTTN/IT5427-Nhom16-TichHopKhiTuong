# Data Dictionary

(docs/03 Tuần 4 TV2 #2 "Viết Data Dictionary đầy đủ") — liệt kê 100% cột trong 2 bảng chính
`WeatherObs` (fact, `ingestion/parsers.py::WEATHEROBS_COLUMNS`) và `Location` (dimension,
`warehouse/location.py`). Đối chiếu trực tiếp với code — không chỉnh tay tách rời khỏi schema thật.

## Bảng WeatherObs (fact — 15 cột gốc + 2 cột phái sinh khi ghi Parquet)

| Cột | Kiểu | Đơn vị | Nguồn gốc / Ghi chú |
|---|---|---|---|
| `location_id` | string | — | Khóa ngoại tới `Location.location_id`. GHCN dạng `VMM00048820`, ISD dạng `48820099999` (USAF+WBAN nối chuỗi), điểm cố định dạng tên (`hanoi`...) |
| `timestamp_utc` | datetime | UTC | Toàn bộ 5 nguồn đã chuẩn hoá về UTC khi parse |
| `source` | string | — | 1 trong 5 giá trị: `GHCN`, `ISD`, `OPEN_METEO`, `ERA5`, `NASA_POWER` |
| `temp_c` | float | °C | GHCN: TAVG hoặc (TMAX+TMIN)/2 nếu thiếu TAVG; ISD: field `TMP` đã chia 10; ERA5: `t2m` đã trừ 273.15 (K→°C) |
| `rh_pct` | float | % (0–100) | Open-Meteo trực tiếp; ISD/GHCN: tính qua Clausius-Clapeyron từ `temp_c`+`dewpoint_c` khi không có trực tiếp |
| `dewpoint_c` | float | °C | ISD field `DEW`; dùng làm input cho công thức Clausius-Clapeyron |
| `precip_mm` | float | mm | GHCN PRCP đã chia 10 (gốc là 1/10mm); ERA5 `tp` đã nhân 1000 (m→mm) |
| `wind_speed_ms` | float | m/s | ISD field `WND` phần speed đã chia 10; ERA5 tính từ `sqrt(u10²+v10²)` |
| `wind_dir_deg` | float | độ (0–360, quy ước khí tượng: hướng gió THỔI TỪ) | ERA5 tính qua `atan2(-u,-v)` |
| `pressure_surface_hpa` | float | hPa | NASA POWER field `PS` (gốc kPa, đã ×10) — **khác `pressure_msl_hpa`, không được gộp** |
| `pressure_msl_hpa` | float | hPa | Open-Meteo/ISD field mực nước biển trung bình — **khác `pressure_surface_hpa`** |
| `solar_rad_wm2` | float | W/m² | NASA POWER field bức xạ (gốc MJ/m²/ngày, đã quy đổi) |
| `cloud_cover_pct` | float | % (0–100) | Open-Meteo trực tiếp |
| `soil_temp_c` | float | °C | Hiện chưa có nguồn thật cung cấp đủ tin cậy — luôn `NaN` (cột dự phòng cho ERA5-Land tương lai) |
| `soil_moist_m3m3` | float | m³/m³ | Tương tự `soil_temp_c` — cột dự phòng, hiện `NaN` |
| `year` *(phái sinh)* | int | — | `YEAR(timestamp_utc)`, dùng làm partition key |
| *(partition theo `source`)* | — | — | Partition thứ 2, tạo 88 thư mục con thật |

## Bảng Location (dimension — 6 cột, 119 dòng)

| Cột | Kiểu | Đơn vị | Ghi chú |
|---|---|---|---|
| `location_id` | string | — | Khóa chính. 113 trạm thật (GHCN+ISD) + 6 điểm cố định (NASA POWER/Open-Meteo) |
| `lat` | float | độ thập phân (-90..90) | |
| `lon` | float | độ thập phân (-180..180) | |
| `elevation_m` | float (nullable) | mét | `NULL` cho 6 điểm cố định (không có cao độ chính thức trong nguồn gốc) |
| `type` | string | — | `station` (113) hoặc `point` (6) |
| `country` | string | — | 1 trong 9 nước ĐNA |

## Bảng EntityResolution (phụ trợ, Tuần 3 — `warehouse/entity_resolution.py`)

| Cột | Kiểu | Ghi chú |
|---|---|---|
| `entity_id` | string | Khóa nhân tạo `ENT_001`... cho 1 vị trí vật lý được 2 nguồn cùng đo |
| `ghcn_id` | string | FK tới `Location.location_id` (nguồn GHCN) |
| `isd_id` | string | FK tới `Location.location_id` (nguồn ISD) |
| `distance_km` | float | Khoảng cách Haversine thật giữa 2 tọa độ gốc — 0 nghĩa là trùng tọa độ WMO |

## Quy ước đặt tên

- Tên cột: `snake_case`, hậu tố đơn vị khi không hiển nhiên (`_hpa`, `_ms`, `_wm2`, `_pct`, `_m3m3`).
- `_surface_` và `_msl_` luôn tách riêng cho áp suất — nhầm lẫn 2 đại lượng này là lỗi tích hợp đã
  phát hiện và sửa ở Tuần 1 (xem `docs/06`).
