# Data Quality Report (TV2 #8, Tuần 3)

Sinh tự động từ `warehouse/data_quality_report.py`, chạy thật trên `warehouse/output/weatherobs.parquet` ngày 2026-11-09. Tổng 9,348,470 bản ghi.

## 1. Tỷ lệ Missing theo nguồn (%)

| source     |   n_records |   temp_c_missing_pct |   rh_pct_missing_pct |   precip_mm_missing_pct |   wind_speed_ms_missing_pct |   pressure_msl_hpa_missing_pct |
|:-----------|------------:|---------------------:|---------------------:|------------------------:|----------------------------:|-------------------------------:|
| ERA5       |     4954824 |                  0   |                100   |                     0   |                         0   |                            0   |
| ISD        |     3464430 |                  0.1 |                  0.3 |                   100   |                         0.8 |                           83.3 |
| GHCN       |      655166 |                  4.1 |                100   |                    41.3 |                       100   |                          100   |
| OPEN_METEO |      263088 |                  0   |                  0   |                     0   |                         0   |                            0   |
| NASA_POWER |       10962 |                  0   |                  0   |                     0   |                         0   |                          100   |

## 2. Tỷ lệ Outlier (IQR, Tukey's fences) theo nguồn (%, trên số bản ghi không null)

| source     |   temp_c_outlier_pct |   rh_pct_outlier_pct |   precip_mm_outlier_pct |   wind_speed_ms_outlier_pct |   pressure_msl_hpa_outlier_pct |
|:-----------|---------------------:|---------------------:|------------------------:|----------------------------:|-------------------------------:|
| GHCN       |                 7.6  |               nan    |                   16.19 |                      nan    |                         nan    |
| ISD        |                 4.32 |                 0.65 |                  nan    |                        0.72 |                           3.28 |
| ERA5       |                 4.92 |               nan    |                   15.03 |                        2.95 |                           4.01 |
| NASA_POWER |                 8.95 |                 7.94 |                    7.63 |                        1.17 |                         nan    |
| OPEN_METEO |                 3.76 |                 0.88 |                   15.07 |                        2.02 |                           6.7  |

Lưu ý phương pháp: dùng IQR thay vì Z-score làm chỉ số chính vì IQR bền vững hơn với outlier cực đoan (xem `ingestion/veracity.py` — Z-score bị hiệu ứng "masking": outlier cực đoan tự làm std phình to, che giấu chính nó). Outlier ở đây chỉ được GẮN CỜ, không tự động xoá — một số giá trị "outlier" thống kê là hiện tượng thời tiết cực đoan có thật (bão, đợt nắng nóng), không phải lỗi dữ liệu.

## 3. Độ phủ không gian-thời gian theo nguồn

| source     |   n_locations | date_min   | date_max   |   n_days_span |
|:-----------|--------------:|:-----------|:-----------|--------------:|
| GHCN       |            41 | 1943-01-01 | 2026-10-07 |         30596 |
| ISD        |            26 | 2015-01-01 | 2024-12-31 |          3653 |
| ERA5       |           113 | 2020-01-01 | 2024-12-31 |          1827 |
| NASA_POWER |             6 | 2020-01-01 | 2024-12-31 |          1827 |
| OPEN_METEO |             6 | 2020-01-01 | 2024-12-31 |          1827 |
