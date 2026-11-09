# Data Quality Report (TV2 #8, Tuần 3)

Sinh tự động từ `warehouse/data_quality_report.py`, chạy thật trên `warehouse/output/weatherobs.parquet` ngày 2026-11-09. Tổng 1,076,473 bản ghi.

## 1. Tỷ lệ Missing theo nguồn (%)

| source     |   n_records |   temp_c_missing_pct |   rh_pct_missing_pct |   precip_mm_missing_pct |   wind_speed_ms_missing_pct |   pressure_msl_hpa_missing_pct |
|:-----------|------------:|---------------------:|---------------------:|------------------------:|----------------------------:|-------------------------------:|
| GHCN       |      655164 |                  4.1 |                100   |                    41.3 |                         100 |                          100   |
| ISD        |      358273 |                  0   |                  0.4 |                   100   |                           0 |                           81.8 |
| OPEN_METEO |       52704 |                  0   |                  0   |                     0   |                           0 |                            0   |
| ERA5       |        8136 |                  0   |                100   |                     0   |                           0 |                          100   |
| NASA_POWER |        2196 |                  0   |                  0   |                     0   |                           0 |                          100   |

## 2. Tỷ lệ Outlier (IQR, Tukey's fences) theo nguồn (%, trên số bản ghi không null)

| source     |   temp_c_outlier_pct |   rh_pct_outlier_pct |   precip_mm_outlier_pct |   wind_speed_ms_outlier_pct |   pressure_msl_hpa_outlier_pct |
|:-----------|---------------------:|---------------------:|------------------------:|----------------------------:|-------------------------------:|
| GHCN       |                 7.6  |               nan    |                   16.19 |                      nan    |                         nan    |
| ERA5       |                 1.35 |               nan    |                   15.03 |                        3.17 |                         nan    |
| ISD        |                 2.36 |                 0.64 |                  nan    |                        1.69 |                           3.37 |
| NASA_POWER |                 9.34 |                 7.7  |                    7.56 |                        1    |                         nan    |
| OPEN_METEO |                 3.21 |                 0.58 |                   14.55 |                        1.73 |                           6.33 |

Lưu ý phương pháp: dùng IQR thay vì Z-score làm chỉ số chính vì IQR bền vững hơn với outlier cực đoan (xem `ingestion/veracity.py` — Z-score bị hiệu ứng "masking": outlier cực đoan tự làm std phình to, che giấu chính nó). Outlier ở đây chỉ được GẮN CỜ, không tự động xoá — một số giá trị "outlier" thống kê là hiện tượng thời tiết cực đoan có thật (bão, đợt nắng nóng), không phải lỗi dữ liệu.

## 3. Độ phủ không gian-thời gian theo nguồn

| source     |   n_locations | date_min   | date_max   |   n_days_span |
|:-----------|--------------:|:-----------|:-----------|--------------:|
| GHCN       |            41 | 1943-01-01 | 2026-10-06 |         30595 |
| ERA5       |           113 | 2021-06-15 | 2021-06-17 |             3 |
| ISD        |            26 | 2024-01-01 | 2024-12-31 |           366 |
| NASA_POWER |             6 | 2024-01-01 | 2024-12-31 |           366 |
| OPEN_METEO |             6 | 2024-01-01 | 2024-12-31 |           366 |
