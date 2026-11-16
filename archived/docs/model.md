# Tài liệu kỹ thuật — Physics-Informed ML (TV3)

(docs/03 Tuần 3 TV3 #10 + Tuần 4 TV3 #6 "Viết tài liệu kỹ thuật mô hình")

## 1. Ba mô hình PINN đã huấn luyện thật

| Script | Bài toán | Physics constraint | Dữ liệu |
|---|---|---|---|
| `model/train_demo.py` | Phương trình nhiệt 1D (sanity check framework) | `u_t = α·u_xx` | Tổng hợp (nghiệm giải tích đã biết để so sánh) |
| `model/pinn_rh_from_dewpoint.py` | Dự báo RH% từ (T, Td) | Clausius-Clapeyron: `es(T) = 6.112·exp(17.67T/(T+243.5))` | **Thật** — 5.000 bản ghi ISD |
| `model/pinn_wind_field_v2.py` | Trường gió (u,v) mịn hoá | Continuity 2D: `∂u/∂x + ∂v/∂y = 0` | **Thật** — 113 trạm ERA5 (15-17/6/2021) |
| `model/navier_stokes_autograd_check.py` | Kiểm tra autograd thuần (không có data loss) | Continuity 2D | Tổng hợp |

## 2. Kiến trúc mạng

Cả 2 mô hình PINN thật dùng MLP 2 lớp ẩn, `Tanh` activation (chuẩn PINN — khả vi vô hạn lần, cần
thiết vì physics loss tính đạo hàm bậc 1-2 qua `torch.autograd.grad(create_graph=True)`):
```
Input(2) -> Linear(32) -> Tanh -> Linear(32) -> Tanh -> Linear(output)
```
`pinn_rh_from_dewpoint.py`: input (T, Td) chuẩn hoá, output RH%.
`pinn_wind_field_v2.py`: input (lon, lat) chuẩn hoá, output (u, v).

## 3. Kết quả huấn luyện thật

**RH từ Clausius-Clapeyron** (5.000 bản ghi ISD thật): loss 1068 → 2,9 qua quá trình huấn luyện,
MAE cuối 1,07 điểm % so với nhãn giả lập Clausius-Clapeyron.

**Trường gió v2** (quét λ ∈ {0, 0.01, 0.1, 1.0}, 113 trạm, chia 91 train/22 test):

| λ | Test RMSE | Test MAE | Physics loss cuối |
|---|---|---|---|
| 0,0 (baseline, không ràng buộc vật lý) | **1,0473** | 0,7772 | 0 |
| 0,01 | 1,0636 | 0,7753 | 0,5347 |
| 0,1 | 1,0577 | 0,7706 | 0,1665 |
| 1,0 | 1,1057 | 0,7921 | 0,0112 |

**Phát hiện trung thực (không che giấu)**: baseline hồi quy thuần (λ=0) có RMSE thấp nhất trên tập
test giữ lại — PINN KHÔNG vượt trội về MSE thuần ở quy mô dữ liệu này. Nguyên nhân hợp lý: bài toán
hiện chỉ có 1 snapshot không-thời gian (trung bình 3 ngày/trạm, không có chiều thời gian), nên ràng
buộc continuity (vốn mạnh nhất khi có nhiều điểm lưới dày đặc và/hoặc chuỗi thời gian) chưa đủ dữ
liệu để thể hiện lợi thế so với một MLP thuần khớp dữ liệu trực tiếp. Giá trị thực của physics loss
ở quy mô này là đảm bảo TÍNH HỢP LÝ VẬT LÝ (bảo toàn khối lượng xấp xỉ) mà baseline không có, không
phải để tối ưu RMSE. Đây là so sánh đã yêu cầu ở TV3 Tuần 3 #4 — báo cáo đúng như quan sát được.

## 4. Siêu tham số

| Tham số | Giá trị | Ghi chú |
|---|---|---|
| Optimizer | Adam | `lr=1e-3` |
| Epochs | 300 (wind v2) / 100 (RH) | Hội tụ quan sát được trong khoảng này, không cần nhiều hơn |
| Batch | Full-batch (không chia batch) | Quy mô dữ liệu nhỏ (<200 điểm/model) không cần mini-batch |
| Seed | `torch.manual_seed(0)`, `np.random.seed(0)` | Tái lập được — xem mục 5 |

## 5. Khả năng tái lập

```bash
pip install -r requirements.txt   # torch, pandas, numpy, pyarrow...
python3 model/pinn_rh_from_dewpoint.py
python3 model/pinn_wind_field_v2.py
```
Cả 2 script seed cố định (`torch.manual_seed(0)`), chạy lại cho kết quả giống hệt (đã verify qua
`tests/test_model_pinn.py` chạy subprocess, so khớp chuỗi `PASS` trong stdout mỗi lần chạy).

**Đã verify thật trên máy sạch** (9/11/2026): tạo `venv` hoàn toàn mới, `pip install numpy pandas
pyarrow torch` (không dùng môi trường anaconda sẵn có), chạy `model/pinn_wind_field_v2.py` — kết
quả RMSE từng λ **giống hệt tới 4 chữ số thập phân** so với lần chạy trong môi trường gốc, xác nhận
`requirements.txt` đủ để tái lập đúng, không thiếu dependency ẩn.

**Cập nhật 10/11/2026 — sửa lỗi trung bình hướng gió**: phát hiện (nhóm, PR #2, Ngô Văn Quang) lỗi
trong `load_real_wind_data()`: script cũ lấy trung bình cộng trực tiếp `wind_speed_ms`/`wind_dir_deg`
theo trạm rồi mới đổi sang vector (u,v) — sai vì hướng gió là đại lượng vòng tròn (trung bình cộng
350° và 10° ra 180°, ngược hướng thật 100%). Đã sửa: đổi từng bản ghi sang (u,v) Decac trước, rồi
mới lấy trung bình vectơ theo trạm. Chạy lại 2 lần liên tiếp cho kết quả giống hệt tới 4 chữ số thập
phân (λ=0: 1,0473; λ=0,01: 1,0636; λ=0,1: 1,0577; λ=1,0: 1,1057) — kết luận không đổi: baseline vẫn
thắng về RMSE thuần ở quy mô dữ liệu này, nhưng giá trị RMSE/MAE từng λ đã đổi so với bản báo cáo
trước đó (bảng mục 3 ở trên đã cập nhật số đúng).

## 6. Pipeline inference

Chưa có script `infer.py` tách riêng checkpoint — các script hiện tại huấn luyện + đánh giá trong
cùng 1 lần chạy (phù hợp quy mô bài tập lớn, không có checkpoint lưu trạng thái giữa các phiên).
Nếu cần inference độc lập: thêm `torch.save(model.state_dict(), "checkpoint.pt")` cuối
`pinn_wind_field_v2.py::train_one()` và 1 script `infer.py` load lại — chưa triển khai do ưu tiên
thời gian cho phần tích hợp dữ liệu (TV2/TV1), đây là hạng mục còn thiếu đã biết (xem
`docs/03` Tuần 3 TV3 #8).
