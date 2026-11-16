# Tài liệu kỹ thuật — Schema & Warehousing (TV2)

(docs/03 Tuần 3 TV2 #10 "Cập nhật tài liệu kỹ thuật Schema & Warehousing")

## 1. Kiến trúc

```
5 nguồn thô → ingestion/parsers.py (PIVOT/PARSE) → Mediated Schema WeatherObs
            → warehouse/survivorship.py (resolve conflict theo ưu tiên nguồn)
            → warehouse/build_warehouse.py (Spark, ghi Parquet partition year/source)
            → warehouse/output/weatherobs.parquet (1.076.473 dòng, 88 partition)
```

Dimension `Location` (`warehouse/location.py`) — 119 vị trí (113 trạm + 6 điểm), referential
integrity 100% đã test tại `tests/test_location.py`.

## 2. Chạy ví dụ query thật

```python
import pandas as pd
df = pd.read_parquet("warehouse/output/weatherobs.parquet")

# Nhiệt độ trung bình theo nguồn
df.groupby("source")["temp_c"].mean()

# Lọc 1 trạm, 1 khoảng thời gian
hanoi = df[(df["location_id"] == "VMM00048820") &
           (df["timestamp_utc"] >= "2021-06-15") &
           (df["timestamp_utc"] <= "2021-06-17")]
```

Qua Spark SQL (sau khi `export JAVA_HOME=...`, xem README mục 6b):
```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("demo").getOrCreate()
spark.read.parquet("warehouse/output/weatherobs.parquet").createOrReplaceTempView("weatherobs")
spark.sql("SELECT source, AVG(temp_c) FROM weatherobs GROUP BY source").show()
```

## 3. Entity Resolution GHCN ↔ ISD (gap đã giải quyết Tuần 3)

GHCN và ISD dùng 2 hệ mã trạm độc lập cho cùng 1 vị trí vật lý (vd Hà Nội: `VMM00048820` vs
`48820099999`). `warehouse/entity_resolution.py` so khớp bằng khoảng cách Haversine (nearest
neighbor 1-1, ngưỡng 5km). **Kết quả thật**: 22/26 trạm ISD khớp được với GHCN (khoảng cách trung
bình 0.53km, nhiều cặp khớp chính xác 0.000km — cùng tọa độ WMO gốc). 4 trạm ISD còn lại không có
GHCN tương ứng trong ngưỡng — hợp lý vì 2 mạng lưới không phủ 100% cùng tập trạm.

## 4. Kiểm chuẩn sai số nội suy không gian (Cross-Validation)

`warehouse/validate_interpolation.py` so sánh giá trị ERA5-Bilinear-nội-suy-vào-tọa-độ-trạm với
giá trị trạm thật đo được (GHCN/ISD), cùng vị trí, cùng ngày — trạm "bị bỏ lại" không được dùng
làm input cho nội suy (Bilinear chỉ đọc lưới ERA5, không biết trạm) nên đây là tập kiểm chứng độc
lập đúng nghĩa leave-one-out.

**Kết quả thật** (104 cặp, 35 trạm, cửa sổ 15–17/6/2021):

| Biến | RMSE | MAE |
|---|---|---|
| `temp_c` | 1,02°C | 0,80°C |
| `precip_mm` | 10,98mm | 5,07mm |

Theo tercile độ cao (proxy địa hình): RMSE nhiệt độ tăng dần theo độ cao (0,88°C → 1,19°C ở nhóm
cao nhất) — hợp lý vật lý (hiệu ứng orographic, lưới ERA5 thô 0,25° không bắt được chi tiết địa
hình). Sai số mưa cao hơn nhiều so với nhiệt độ — đúng với y văn (reanalysis luôn kém hơn nhiều ở
biến mưa so với nhiệt độ, xem trích dẫn trong `docs/12`).

## 5. Partitioning — phát hiện ngược kỳ vọng (giữ nguyên, đã ghi nhận)

Partition theo `year/source` **chậm hơn** ~2,2 lần và **tốn dung lượng hơn** ~3,4 lần so với không
partition, ở quy mô ~1 triệu dòng hiện tại (xem `docs/10` mục 2 để biết chi tiết + nguyên nhân).
Giữ nguyên partition key — lợi ích dự kiến rõ hơn khi dữ liệu đạt quy mô ERA5 full 5 năm (~35GB).

## 6. Data Quality Report

Sinh tự động bởi `warehouse/data_quality_report.py` → `docs/13-data-quality-report.md` — tỷ lệ
missing/outlier/độ phủ không gian-thời gian thật theo từng nguồn. Phát hiện đáng chú ý: GHCN có
100% missing ở `rh_pct`/`wind_speed_ms`/`pressure_msl_hpa` (GHCN-Daily về bản chất chỉ báo cáo
TMAX/TMIN/PRCP, không phải lỗi parser) — đây là giới hạn cấu trúc nguồn, không phải lỗi pipeline.

## 7. Data Dictionary

Xem `data_dictionary.md` ở thư mục gốc — liệt kê đầy đủ 15 cột `WeatherObs` + 6 cột `Location`,
đơn vị, nguồn gốc.
