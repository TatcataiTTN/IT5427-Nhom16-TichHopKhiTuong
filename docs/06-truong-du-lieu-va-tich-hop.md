# Trường dữ liệu từng nguồn, Mediated Schema, và các điểm cần quyết định tích hợp

Tài liệu này trả lời 3 câu hỏi bằng dữ liệu **thật đã kiểm chứng** (không suy đoán, xem `05-bao-cao-kiem-tra-nguon-du-lieu.md`), áp dụng đúng khung lý thuyết trong `slides/2_SchemaAlignment.pdf` (GAV/LAV) và `slides/3_RecordLinkage_ER.pdf` (Similarity/Survivorship, Physics-Informed Integration):

1. Mỗi nguồn có trường (field) gì?
2. Mediated Schema nên thiết kế ra sao, map theo GAV như thế nào?
3. Đâu là chỗ **trùng lặp dữ liệu** cần quyết định tích hợp (Survivorship)?
4. Đâu là **khoảng trống vật lý** thật sự cần PINN, phân biệt với chỗ chỉ cần nội suy không gian thông thường (Kriging/Bilinear)?

---

## 1. Trường dữ liệu thật của từng nguồn (đã gọi API/tải mẫu để lấy đúng tên trường)

### NASA POWER (điểm, mô hình vệ tinh MERRA-2/CERES/GEOS, `community=AG`)

| Trường | Ý nghĩa | Đơn vị |
|---|---|---|
| T2M, T2M_MAX, T2M_MIN | Nhiệt độ 2m (TB/max/min) | °C |
| RH2M | Độ ẩm tương đối 2m | % |
| QV2M | Độ ẩm riêng 2m | g/kg |
| T2MDEW | Điểm sương 2m | °C |
| PRECTOTCORR | Lượng mưa đã hiệu chỉnh | mm/ngày |
| WS2M, WS10M | Tốc độ gió 2m/10m (**vô hướng**, đã gộp hướng) | m/s |
| PS | Áp suất **bề mặt** | kPa |
| ALLSKY_SFC_SW_DWN, CLRSKY_SFC_SW_DWN | Bức xạ mặt trời (có mây / trời quang) | MJ/m²/ngày |

### Open-Meteo Historical (điểm, nội suy từ ERA5/ICON/GFS)

| Trường | Ý nghĩa | Đơn vị |
|---|---|---|
| temperature_2m | Nhiệt độ 2m | °C |
| relative_humidity_2m | Độ ẩm tương đối 2m | % |
| precipitation, rain | Mưa (tổng / mưa lỏng riêng) | mm |
| pressure_msl | Áp suất **mực nước biển** (MSL) | hPa |
| cloud_cover | Độ che phủ mây | % |
| wind_speed_10m, wind_direction_10m | Tốc độ + **hướng gió** (2 trường riêng) | m/s, ° |
| shortwave_radiation | Bức xạ sóng ngắn | W/m² |
| soil_temperature_0_to_7cm, soil_moisture_0_to_7cm | Nhiệt độ/độ ẩm đất | °C, m³/m³ |
| et0_fao_evapotranspiration | Bốc thoát hơi tham chiếu | mm |

### NOAA GHCN-Daily (trạm điểm, dạng "long" — 1 dòng/1 biến/1 ngày)

Cấu trúc: `ID, DATE, ELEMENT, DATA_VALUE, M_FLAG, Q_FLAG, S_FLAG, OBS_TIME` — các `ELEMENT` thường gặp: `TMAX, TMIN, TAVG, PRCP, SNOW, SNWD`. **Đây là dạng "long/EAV" (Entity-Attribute-Value)** — khác hẳn 4 nguồn kia đang ở dạng "wide" (mỗi biến 1 cột) → **cần pivot** trước khi đưa vào Mediated Schema.

### NOAA ISD / Global Hourly (trạm điểm, có cả METAR gốc)

Header thật: `STATION, DATE, SOURCE, LATITUDE, LONGITUDE, ELEVATION, NAME, REPORT_TYPE, CALL_SIGN, QUALITY_CONTROL, WND, CIG, VIS, TMP, DEW, SLP, ED1, GA1-4, GE1, GF1, MA1, MW1-2, OC1, REM, EQD`

- `WND`, `TMP`, `DEW`, `SLP`, `VIS`, `CIG`, `MA1` là các trường **"nén"** — mỗi ô chứa nhiều sub-field ngăn cách bởi dấu phẩy bên trong (VD `TMP="+0250,1"` = nhiệt độ 25.0°C + flag chất lượng `1`). **Cần parse riêng từng trường trước khi dùng** — đây chính xác là "Syntactic/Format Heterogeneity" ở buổi 2.
- `REM` chứa nguyên văn bản tin **METAR gốc** (VD `VVTS 010000Z VRB01KT 6000 FEW020 25/25 Q1012 NOSIG`) — nguồn dự phòng để đối chiếu chéo khi các trường có cấu trúc bị lỗi parse.
- `SLP` là áp suất **mực nước biển** (giống Open-Meteo, khác POWER).

### ERA5 (lưới, ARCO-ERA5, đã xác nhận đủ 35 biến thật)

Nhóm liên quan trực tiếp đề tài: `2m_temperature, 10m_u_component_of_wind, 10m_v_component_of_wind, surface_pressure, mean_sea_level_pressure, specific_humidity, total_precipitation, total_cloud_cover, toa_incident_solar_radiation, total_column_water_vapour, temperature` (đa tầng áp suất qua chiều `level`), `u_component_of_wind, v_component_of_wind, vertical_velocity` (đa tầng), `sea_surface_temperature, land_sea_mask, soil_type`...

- **Gió ở ERA5 là dạng vector (u,v)** — khác POWER (chỉ có tốc độ vô hướng WS10M) và khác Open-Meteo (tốc độ + hướng, dạng cực).
- **ERA5 có cả `surface_pressure` VÀ `mean_sea_level_pressure`** — 2 đại lượng vật lý khác nhau, khớp lần lượt với POWER (PS = surface) và Open-Meteo/ISD (pressure_msl/SLP = mực nước biển).
- **ERA5 có chiều `level`** (nhiều tầng áp suất) — 4 nguồn còn lại chỉ có dữ liệu bề mặt/2m, không có hồ sơ theo độ cao.

---

## 2. Mediated Schema đề xuất — áp dụng đúng khung GAV trong slide Schema Alignment

Theo đúng cấu trúc slide (`Global-as-View`, slide 23–26: `Movie(title,director,year,genre) ⊇ S1.Movie(...) ∪ S5.MovieGenres(...) ∪ ...`), Mediated Schema cho project nên là:

```
WeatherObs(location_id, timestamp_utc, source,
           temp_c, rh_pct, dewpoint_c,
           precip_mm, wind_speed_ms, wind_dir_deg,
           pressure_surface_hpa, pressure_msl_hpa,
           solar_rad_wm2, cloud_cover_pct, soil_temp_c, soil_moist_m3m3)

Location(location_id, lat, lon, elevation_m, type ∈ {station, grid_cell}, country)
```

**Mapping GAV cho từng nguồn** (mediated ⊇ nguồn, giống hệt công thức slide 25):

```
WeatherObs(loc,t,'NASA_POWER',temp,rh,dew,precip,ws,NULL,ps,NULL,rad,NULL,NULL,NULL) ⊇
    POWER(loc,t,T2M,RH2M,T2MDEW,PRECTOTCORR,WS10M,PS,ALLSKY_SFC_SW_DWN)

WeatherObs(loc,t,'OPEN_METEO',temp,rh,NULL,precip,ws,wd,NULL,pmsl,rad,cc,soilT,soilM) ⊇
    OpenMeteo(loc,t,temperature_2m,relative_humidity_2m,precipitation,
              wind_speed_10m,wind_direction_10m,pressure_msl,shortwave_radiation,
              cloud_cover,soil_temperature_0_to_7cm,soil_moisture_0_to_7cm)

WeatherObs(loc,t,'GHCN',tmax,tmin,tavg,precip,...) ⊇
    PIVOT(GHCN(id,date,element,value) WHERE element IN ('TMAX','TMIN','TAVG','PRCP'))
    -- buoc PIVOT bat buoc vi GHCN dang "long", 4 nguon con lai dang "wide"

WeatherObs(loc,t,'ISD',temp,dew,ws,wd,pmsl,vis,...) ⊇
    PARSE(ISD(station,date,WND,TMP,DEW,SLP,VIS,MA1))
    -- buoc PARSE bat buoc vi cac truong ISD la chuoi nen nhieu sub-field

WeatherObs(loc,t,'ERA5',temp,NULL,NULL,precip,ws=f(u,v),wd=g(u,v),ps,pmsl,rad,cc,NULL,NULL) ⊇
    ERA5(lat,lon,t,'2m_temperature','total_precipitation',
         '10m_u_component_of_wind','10m_v_component_of_wind',
         surface_pressure,mean_sea_level_pressure,surface_solar_radiation_downwards,total_cloud_cover)
    -- (13/10/2026) rad dung surface_solar_radiation_downwards (buc xa TAI BE MAT, cung dai luong voi
    --  POWER ALLSKY_SFC_SW_DWN va Open-Meteo shortwave_radiation), KHONG dung toa_incident_solar_radiation
    --  (buc xa o DINH khi quyen). Don vi: J/m2 tich luy 1 gio -> chia 3600 ra W/m2
    -- can chuyen doi vector (u,v) -> (speed,direction): ws=sqrt(u²+v²), wd=atan2(-u,-v)
```

---

## 3. Khoảng trùng lặp dữ liệu cần quyết định tích hợp (Record Linkage / Survivorship)

Đây là những chỗ **≥ 2 nguồn cùng đo 1 đại lượng** tại cùng vị trí/thời điểm — đúng bài toán buổi 4 (không phải "trùng bản ghi" như khử trùng lặp tin đăng, mà là "trùng giá trị đo" cần **Survivorship rule** như slide đã nêu ở mục Record Linkage → Entity Resolution → Data Fusion, xem `1. Introduction.pdf` slide 46).

| Đại lượng | Nguồn trùng | Vấn đề khi tích hợp | Quyết định cần làm |
|---|---|---|---|
| **Nhiệt độ 2m** | POWER, Open-Meteo, GHCN, ISD, ERA5 (**cả 5 nguồn**) | Trạm (GHCN/ISD) đo thật tại điểm; POWER/Open-Meteo/ERA5 là mô hình/nội suy — độ lệch có thể vài °C ở vùng địa hình phức tạp | **Survivorship**: ưu tiên trạm (ISD/GHCN) làm ground truth khi có; dùng ERA5/POWER/Open-Meteo khi trạm thiếu dữ liệu (missing-value policy dựa trên độ tin cậy nguồn, đúng khái niệm "Veracity" buổi 2) |
| **Áp suất** | POWER (`PS`, bề mặt) vs Open-Meteo/ISD (`pressure_msl`/`SLP`, mực nước biển) vs ERA5 (**có cả 2**) | ⚠️ **Đây không phải cùng 1 đại lượng vật lý** — bề mặt và mực nước biển lệch nhau theo độ cao trạm (công thức khí áp chuẩn). Nếu so trực tiếp POWER.PS với Open-Meteo.pressure_msl sẽ **sai hoàn toàn**, giống lỗi "Celsius vs Fahrenheit" ở slide Data-level Heterogeneity | Bắt buộc **chuẩn hoá về cùng 1 loại áp suất** trước khi so khớp (dùng elevation trong `Location` để quy đổi qua công thức barometric), hoặc giữ cả 2 cột `pressure_surface` và `pressure_msl` riêng trong Mediated Schema như đã thiết kế ở mục 2 |
| **Gió** | POWER (`WS10M`, vô hướng), Open-Meteo (tốc độ+hướng, dạng cực), ISD (`WND` mã hoá), ERA5 (`u,v` dạng vector) | 3 cách biểu diễn khác nhau (vô hướng / cực / Descartes) — không thể so trực tiếp | Chuẩn hoá tất cả về dạng (speed, direction); khi so ERA5 với trạm cần **decompose u,v → speed/direction trước** |
| **Mưa** | POWER, Open-Meteo, GHCN (`PRCP`), ERA5 (`total_precipitation`) | Mưa đối lưu nhiệt đới (đặc trưng ĐNA) có độ lệch không gian rất lớn giữa mô hình và thực đo — đây là biến **Veracity thấp nhất** trong 5V | Không dùng trung bình đơn giản; nên dùng **trạm làm ground truth khi có**, ERA5/vệ tinh (CHIRPS nếu bổ sung) chỉ để lấp khoảng trống không có trạm — cần task riêng đo RMSE/MAE giữa các nguồn (đã có sẵn trong `03-ke-hoach-160-tasks.md`, Tuần 3, TV2 #3-4) |
| **Độ ẩm** | POWER (`RH2M`, `QV2M` — 2 dạng), Open-Meteo (`RH%`), ISD (chỉ có `DEW`, **không có RH trực tiếp**), ERA5 (`specific_humidity`, không có RH trực tiếp) | 3 dạng biểu diễn độ ẩm khác nhau (RH%, specific humidity g/kg, dew point °C) — **không so trực tiếp được** | Chuẩn hoá tất cả về RH% bằng công thức Clausius-Clapeyron (xem mục 4 — đây vừa là bài toán trùng lặp vừa là bài toán khoảng trống vật lý) |

---

## 4. Khoảng trống vật lý cần PINN — phân biệt rõ với chỗ chỉ cần nội suy không gian thường

Slide `3_RecordLinkage_ER.pdf` không nói PINN (PINN nằm ở đề xuất đề tài + phần "Addressing Big Data challenges" của buổi 3), nhưng đúng theo định nghĩa trong `01-de-xuat-de-tai.md` (Clausius-Clapeyron, Navier-Stokes), **PINN chỉ nên dùng cho những chỗ nội suy tuyến tính/không gian đơn thuần (Kriging/Bilinear) không giải quyết được vì bản chất là thiếu ràng buộc vật lý, không phải thiếu điểm dữ liệu không gian.** Phân biệt rõ 2 loại khoảng trống:

### 4a. Khoảng trống KHÔNG cần PINN — chỉ cần nội suy không gian thông thường (Kriging/Bilinear)

- **Trạm nằm giữa các ô lưới ERA5**: đã có sẵn giải pháp trong đề xuất đề tài — Kriging/Bilinear Interpolation. Đây thuần tuý là bài toán nội suy không gian số học, không cần ràng buộc vật lý gì thêm.

### 4b. Khoảng trống THẬT SỰ cần PINN — nơi thiếu ràng buộc vật lý, không chỉ thiếu điểm

| Khoảng trống | Vì sao nội suy thường KHÔNG đủ | Ràng buộc PINN áp dụng |
|---|---|---|
| **ISD/nhiều trạm chỉ có Dew Point, không có RH%** — nhưng Mediated Schema cần RH% để so với POWER/Open-Meteo | Suy RH từ dew point **không phải phép nội suy** mà là một **phương trình vật lý chính xác** (không tuyến tính, phụ thuộc mũ theo T) — nội suy tuyến tính hay trung bình cộng sẽ cho kết quả sai hệ thống | **Clausius-Clapeyron** — dùng đúng công thức trong đề xuất đề tài: $e_s(T) = 611.2 \exp\left(\frac{17.67(T-273.15)}{T-29.65}\right)$, $RH = e/e_s(T) \times 100$. Đây không phải PINN neural network — có thể tính trực tiếp bằng công thức (PINN chỉ cần thiết nếu muốn **học đồng thời** nhiều biến liên quan có nhiễu, để phần dư của phương trình này trở thành 1 thành phần của loss) |
| **Gió tại vị trí station suy ra từ (u,v) của 4 ô lưới ERA5 lân cận** | Nội suy tuyến tính riêng lẻ u và v **không đảm bảo trường gió nội suy tuân thủ bảo toàn khối lượng/động lượng** — ở vùng ven biển/núi ĐNA (gió biển-đất, hiệu ứng địa hình), nội suy tuyến tính đơn giản dễ tạo ra trường gió phi vật lý (hội tụ/phân kỳ giả) | **Navier-Stokes rút gọn 2D** (đã có công thức trong đề xuất đề tài) ràng buộc gradient áp suất với biến thiên gió — dùng làm Physics Loss khi huấn luyện mô hình nội suy gió mịn hơn lưới ERA5 gốc |
| **Biến không nguồn nào đo trực tiếp tại điểm trạm**: bức xạ mặt trời, độ ẩm đất, bốc thoát hơi (chỉ có ở POWER/Open-Meteo/ERA5 — mô hình/vệ tinh, GHCN/ISD hoàn toàn không đo các biến này) | Đây **không phải khoảng trống không gian** (trạm không "thiếu 1 điểm gần đó" để nội suy) mà là khoảng trống **loại biến hoàn toàn không được quan trắc mặt đất** — không có ground truth nào để nội suy tới | Không dùng nội suy đơn thuần; phải **tin vào mô hình vật lý/vệ tinh** (POWER/ERA5) và dùng PINN/mô hình hồi quy để **hiệu chỉnh (bias-correct)** bằng các biến trạm đo được (T, RH) có tương quan vật lý với bức xạ/bốc thoát hơi (VD phương trình Penman-Monteith cho evapotranspiration) |
| **Mưa đối lưu nhiệt đới** — đã nêu ở mục 3, và slide đề xuất đề tài đã ghi rõ **"không nội suy tuyến tính thông thường"** cho mưa | Mưa có tính "on/off" và biến thiên không gian rất mạnh (khác nhiệt độ biến thiên mượt) — nội suy tuyến tính giữa 2 điểm có mưa/không mưa cho ra "mưa giả" ở giữa | Không phải PINN thuần tuý mà là **chính sách xử lý riêng đã ghi trong đề xuất đề tài**: zero-fill khi cloud cover = 0, hoặc mô hình Markov Chain cho chuỗi mưa — về bản chất đây là "physics-informed missing-value policy", cùng họ tư duy với PINN nhưng đơn giản hơn nhiều, **nên làm trước, chỉ nâng lên PINN đầy đủ nếu còn thời gian** (đúng khuyến nghị "phương án lùi" đã có sẵn trong đề xuất đề tài) |
| **Hồ sơ theo độ cao (vertical profile)** — chỉ ERA5 có (`level` dimension, nhiều tầng áp suất); 4 nguồn còn lại chỉ có dữ liệu bề mặt/2m | Không có nguồn nào khác để đối chiếu/nội suy chéo — đây là **biến chỉ ERA5 độc quyền có** | Không phải vấn đề tích hợp — nếu đề tài cần dùng (VD tính độ bất ổn định khí quyển ảnh hưởng đối lưu/mưa), chỉ dùng trực tiếp từ ERA5, không cần PINN hay nội suy gì |

---

## 5. Tóm tắt hành động cho TV2 (Schema Lead) và TV3 (Spark/PINN Lead)

1. **TV2**: viết đúng 5 script chuẩn hoá theo mục 2 — đặc biệt 2 bước bắt buộc mà 3/5 nguồn không cần: **PIVOT** cho GHCN (long→wide) và **PARSE** cho ISD (giải nén sub-field). Đây là code cụ thể hoá task "ETL Transform" đã có trong `03-ke-hoach-160-tasks.md`.
2. **TV2**: khi thiết kế bảng `WeatherObs`, giữ **riêng 2 cột** `pressure_surface` và `pressure_msl` — không gộp chung, tránh lỗi tích hợp sai ở mục 3.
3. **TV3**: chỉ cần cài đặt PINN thật sự (Clausius-Clapeyron + Navier-Stokes làm Physics Loss) cho **2 trường hợp ở mục 4b** (suy RH từ dew point khi cần dùng đồng thời nhiều nguồn nhiễu, và làm mịn trường gió liên tục từ lưới ERA5) — đây là phạm vi PINN **tối thiểu, khả thi** để chứng minh đúng kỹ thuật đã cam kết trong đề xuất đề tài, không cần làm PINN cho toàn bộ 35 biến.
4. **Cả nhóm**: mục 3 chính là nội dung cần đưa vào `Data Quality Report` (đã có task ở Tuần 3, TV2 #8 trong kế hoạch 160 tác vụ) — dùng đúng bảng ở mục 3 làm khung viết báo cáo.
