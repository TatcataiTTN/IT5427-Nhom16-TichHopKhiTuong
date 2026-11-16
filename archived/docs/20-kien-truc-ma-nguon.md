# Kiến trúc mã nguồn: luồng code cụ thể của dự án

Xem đầy đủ tại [`docs/kien-truc-ma-nguon/index.html`](kien-truc-ma-nguon/index.html) (mở trực tiếp bằng trình duyệt,
không cần server). Trang này tổng hợp:

- 3 sơ đồ (vẽ bằng draw.io, sinh từ code, không vẽ tay): tổng quan 7 tầng xử lý, rồi chi tiết từng tầng kèm tên
  file script thật trong repo.
- Bảng ngôn ngữ/nền tảng dùng trong dự án: Python, Bash, PySpark, Pandas/NumPy, DuckDB, PyTorch, Kafka, Docker,
  Streamlit, LaTeX, Matplotlib, pytest — mỗi dòng kèm file thật dùng công nghệ đó.

**Nguồn dữ liệu cho sơ đồ:** thứ tự lệnh chạy thật trong mục "Chạy toàn bộ" của `README.md`, đối chiếu với cây
thư mục thật (`scripts/`, `ingestion/`, `warehouse/`, `model/`, `dashboard/`, `tests/`) ngày 15/11/2026 — không
suy đoán tên file.

**Tái tạo sơ đồ khi code đổi:**

```bash
cd docs/kien-truc-ma-nguon
python3 src/gen_pages.py        # ghi lại kien-truc-ma-nguon.drawio (3 trang)
drawio --export --format svg --page-index 1 --output trang1-tong-quan.svg kien-truc-ma-nguon.drawio
drawio --export --format svg --page-index 2 --output trang2-chi-tiet-A-D.svg kien-truc-ma-nguon.drawio
drawio --export --format svg --page-index 3 --output trang3-chi-tiet-E-G.svg kien-truc-ma-nguon.drawio
```

Mở `kien-truc-ma-nguon.drawio` trực tiếp bằng app draw.io/diagrams.net nếu muốn sửa tay thay vì sửa code.
