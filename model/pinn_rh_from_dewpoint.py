#!/usr/bin/env python3
"""
Physics loss Clausius-Clapeyron thử nghiệm trên dữ liệu ISD THẬT (docs/03 Tuần 2 TV3 #6).

Bài toán (docs/06 mục 4b): nhiều trạm ISD chỉ có Dew Point, không có RH% trực tiếp.
`ingestion/parsers.py::clausius_clapeyron_rh()` đã tính RH% bằng CÔNG THỨC TRỰC TIẾP
(đúng khuyến nghị "làm trước, không cần mạng nơ-ron"). File này đi xa hơn 1 bước: huấn
luyện 1 mạng nơ-ron nhỏ dự đoán RH% từ (T, Td), có LOSS VẬT LÝ (physics loss) ép mạng
tuân thủ phương trình Clausius-Clapeyron thay vì chỉ khớp nhãn — đúng tinh thần PINN
("học đồng thời nhiều biến, để phần dư phương trình trở thành 1 thành phần của loss").

Nhãn "data loss" ở đây lấy TRỰC TIẾP từ công thức C-C (vì dữ liệu ISD thật không có RH%
đo trực tiếp để đối chiếu) — mục đích của script là CHỨNG MINH kỹ thuật physics loss
chạy đúng trên dữ liệu thật, không phải để thay thế công thức trực tiếp (vốn đã đủ dùng
và rẻ hơn nhiều, như docs/06 đã phân tích).

Chạy: python3 model/pinn_rh_from_dewpoint.py
"""
import glob
import os
import sys

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ingestion.parsers import clausius_clapeyron_rh, parse_isd

DATA = os.path.join(os.path.dirname(__file__), "..", "data_samples", "batch_week2")
torch.manual_seed(0)


def load_real_training_data(max_rows=5000):
    frames = []
    for fp in sorted(glob.glob(os.path.join(DATA, "isd_global_hourly_2024", "*.csv")))[:5]:
        frames.append(parse_isd(fp))
    df = pd.concat(frames, ignore_index=True)
    df = df.dropna(subset=["temp_c", "dewpoint_c"])
    df = df[df["dewpoint_c"] <= df["temp_c"] + 0.5]  # loai gia tri phi vat ly (Td > T qua nhieu)
    if len(df) > max_rows:
        df = df.sample(max_rows, random_state=0)
    return df.reset_index(drop=True)


class RHNet(nn.Module):
    def __init__(self, hidden=16):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(2, hidden), nn.Tanh(),
            nn.Linear(hidden, hidden), nn.Tanh(),
            nn.Linear(hidden, 1), nn.Sigmoid(),  # output trong (0,1), nhan 100 -> %
        )

    def forward(self, t_td):
        return self.net(t_td) * 100.0


def es_clausius_clapeyron(temp_c: torch.Tensor) -> torch.Tensor:
    """Ap suat hoi bao hoa (hPa), cong thuc giong het ingestion/parsers.py::clausius_clapeyron_rh."""
    return 6.112 * torch.exp(17.67 * temp_c / (temp_c + 243.5))


def main():
    print("== Tai du lieu ISD that (nhiet do + diem suong) ==")
    df = load_real_training_data()
    print(f"So ban ghi that dung de huan luyen: {len(df)}")

    rh_label = clausius_clapeyron_rh(df["temp_c"], df["dewpoint_c"])
    valid = rh_label.notna()
    df, rh_label = df[valid].reset_index(drop=True), rh_label[valid].reset_index(drop=True)

    T = torch.tensor(df["temp_c"].values, dtype=torch.float32).unsqueeze(1)
    Td = torch.tensor(df["dewpoint_c"].values, dtype=torch.float32).unsqueeze(1)
    RH_label = torch.tensor(rh_label.values, dtype=torch.float32).unsqueeze(1)
    X = torch.cat([T, Td], dim=1)

    model = RHNet()
    optimizer = torch.optim.Adam(model.parameters(), lr=5e-3)

    print("\n== Huan luyen: Data Loss + Physics Loss (Clausius-Clapeyron residual) ==")
    losses, data_losses, physics_losses = [], [], []
    for epoch in range(200):
        optimizer.zero_grad()
        rh_pred = model(X)

        loss_data = ((rh_pred - RH_label) ** 2).mean()

        # Physics loss: ep rh_pred/100 * es(T) phai gan bang es(Td) (dinh nghia C-C cua e/es)
        es_T = es_clausius_clapeyron(T)
        es_Td = es_clausius_clapeyron(Td)
        e_implied = (rh_pred / 100.0) * es_T
        residual = e_implied - es_Td
        loss_physics = (residual ** 2).mean() / (es_Td.mean() ** 2)  # chuan hoa ve khong thu nguyen

        loss = loss_data + 0.1 * loss_physics
        if torch.isnan(loss) or torch.isinf(loss):
            raise RuntimeError(f"Loss NaN/Inf o epoch {epoch}")

        loss.backward()
        optimizer.step()
        losses.append(loss.item())
        data_losses.append(loss_data.item())
        physics_losses.append(loss_physics.item())
        if epoch % 40 == 0:
            print(f"  epoch {epoch:3d}: loss={loss.item():.4f} (data={loss_data.item():.4f}, "
                  f"physics={loss_physics.item():.6f})")

    assert losses[-1] < losses[0], "Loss khong giam"
    print(f"\nKiem thu: loss giam {losses[0]:.4f} -> {losses[-1]:.4f}. Khong NaN/Inf. PASS.")

    with torch.no_grad():
        rh_final = model(X)
        mae = (rh_final - RH_label).abs().mean().item()
    print(f"MAE giua RH du doan (mang) va RH tu cong thuc truc tiep: {mae:.2f} diem %")
    print("\n(Luu y: muc dich la xac nhan physics loss chay dung tren du lieu that, khong phai "
          "de thay the cong thuc truc tiep -- xem docs/06 muc 4b ve ly do nay.)")


if __name__ == "__main__":
    main()
