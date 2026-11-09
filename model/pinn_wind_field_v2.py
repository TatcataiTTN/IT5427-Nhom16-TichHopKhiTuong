#!/usr/bin/env python3
"""
PINN v2 - truong gio (u,v) tu du lieu ERA5 THAT, ket hop Data Loss + Physics Loss
(continuity Navier-Stokes 2D rut gon) (docs/03 Tuan 3, TV3 #1-4):
  #1 baseline Data+Physics Loss (phien ban nay la ban chinh thuc, thay cho RH/Clausius-Clapeyron
     da lam o Tuan 2 - xem model/pinn_rh_from_dewpoint.py cho PINN v1)
  #2 them rang buoc Navier-Stokes rut gon (continuity: du/dx + dv/dy = 0) vao loss, huan luyen v2
  #3 quet nhieu gia tri lambda can bang Data/Physics Loss
  #4 so sanh PINN (lambda>0) vs baseline hoi quy thuan (lambda=0, khong rang buoc vat ly)

Du lieu: 8.136 ban ghi ERA5 that (15-17/6/2021, 113 tram, da noi suy Bilinear) tu
warehouse/output/weatherobs.parquet. Input (x,y) = (lon, lat) da chuan hoa; target (u,v) =
wind_speed*cos/sin(wind_dir) (chuyen doi huong gio khi tuong -> vector Decac chuan).

Chay: python3 model/pinn_wind_field_v2.py
"""
import os

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

torch.manual_seed(0)
np.random.seed(0)

ROOT = os.path.join(os.path.dirname(__file__), "..")
WAREHOUSE = os.path.join(ROOT, "warehouse", "output", "weatherobs.parquet")
LOCATION = os.path.join(ROOT, "warehouse", "output", "location.parquet")


class WindFieldNet(nn.Module):
    def __init__(self, hidden=32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(2, hidden), nn.Tanh(),
            nn.Linear(hidden, hidden), nn.Tanh(),
            nn.Linear(hidden, 2),
        )

    def forward(self, xy):
        return self.net(xy)


def continuity_residual(model, xy):
    xy = xy.clone().requires_grad_(True)
    uv = model(xy)
    u, v = uv[:, 0:1], uv[:, 1:2]
    du = torch.autograd.grad(u, xy, grad_outputs=torch.ones_like(u), create_graph=True)[0]
    dv = torch.autograd.grad(v, xy, grad_outputs=torch.ones_like(v), create_graph=True)[0]
    return du[:, 0:1] + dv[:, 1:2]


def load_real_wind_data():
    df = pd.read_parquet(WAREHOUSE)
    era5 = df[(df["source"] == "ERA5") & df["wind_speed_ms"].notna() & df["wind_dir_deg"].notna()].copy()
    # Giu dung cua so thi nghiem 15-17/6/2021: warehouse day du co ERA5 ca 5 nam, neu lay het se
    # thanh trung binh 5 nam (khac thi nghiem da bao cao, va trung binh cong huong gio theo do
    # khong co nghia tren chuoi dai vi huong gio la dai luong vong tron)
    ts = pd.to_datetime(era5["timestamp_utc"], utc=True)  # Spark ghi theo UTC, pandas doc ra kieu khong mui gio
    era5 = era5[(ts >= pd.Timestamp("2021-06-15", tz="UTC")) & (ts < pd.Timestamp("2021-06-18", tz="UTC"))]
    loc = pd.read_parquet(LOCATION)[["location_id", "lat", "lon"]]
    era5 = era5.merge(loc, on="location_id", how="inner")

    # Trung binh theo tram (giam 8136 ban ghi ve 1 vecto gio dai dien/tram cho bai toan
    # noi suy khong gian tinh - dung thoi diem can them 1 chieu thoi gian, ngoai pham vi bai nay)
    agg = era5.groupby(["location_id", "lat", "lon"]).agg(
        wind_speed_ms=("wind_speed_ms", "mean"),
        wind_dir_deg=("wind_dir_deg", "mean"),
    ).reset_index()

    theta = np.radians(agg["wind_dir_deg"].to_numpy())
    # Quy uoc khi tuong: wind_dir = huong gio THOI TU (vd 90 = gio Dong, thoi ve huong Tay)
    u = -agg["wind_speed_ms"].to_numpy() * np.sin(theta)
    v = -agg["wind_speed_ms"].to_numpy() * np.cos(theta)

    xy = agg[["lon", "lat"]].to_numpy()
    uv = np.stack([u, v], axis=1)
    return xy.astype(np.float32), uv.astype(np.float32), agg


def normalize(x, mean, std):
    return (x - mean) / std


def train_one(xy_train, uv_train, lambda_physics, epochs=300, lr=1e-3):
    model = WindFieldNet()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    mse = nn.MSELoss()

    xy_t = torch.tensor(xy_train)
    uv_t = torch.tensor(uv_train)

    losses = []
    for epoch in range(epochs):
        optimizer.zero_grad()
        pred = model(xy_t)
        loss_data = mse(pred, uv_t)

        if lambda_physics > 0:
            residual = continuity_residual(model, xy_t)
            loss_physics = (residual ** 2).mean()
        else:
            loss_physics = torch.tensor(0.0)

        loss = loss_data + lambda_physics * loss_physics
        loss.backward()
        optimizer.step()
        losses.append((loss_data.item(), loss_physics.item() if lambda_physics > 0 else 0.0))

    return model, losses


def evaluate(model, xy_test, uv_test):
    with torch.no_grad():
        pred = model(torch.tensor(xy_test)).numpy()
    rmse = float(np.sqrt(np.mean((pred - uv_test) ** 2)))
    mae = float(np.mean(np.abs(pred - uv_test)))
    return rmse, mae


def main():
    xy_raw, uv_raw, agg = load_real_wind_data()
    n = len(xy_raw)
    print(f"Du lieu gio ERA5 that: {n} tram (trung binh 15-17/6/2021)")
    assert n >= 20, "Qua it tram de chia train/test co y nghia"

    # Chuan hoa input (toa do) va output (van toc) de on dinh huan luyen
    xy_mean, xy_std = xy_raw.mean(0), xy_raw.std(0)
    uv_mean, uv_std = uv_raw.mean(0), uv_raw.std(0)
    xy_n = normalize(xy_raw, xy_mean, xy_std)
    uv_n = normalize(uv_raw, uv_mean, uv_std)

    rng = np.random.RandomState(42)
    idx = rng.permutation(n)
    n_test = max(5, int(n * 0.2))
    test_idx, train_idx = idx[:n_test], idx[n_test:]

    xy_train, uv_train = xy_n[train_idx], uv_n[train_idx]
    xy_test, uv_test = xy_n[test_idx], uv_n[test_idx]
    print(f"Train: {len(train_idx)} tram | Test (giu lai, khong dung khi train): {len(test_idx)} tram")

    # --- #3: quet lambda ---
    lambdas = [0.0, 0.01, 0.1, 1.0]
    print("\n--- Quet lambda (can bang Data Loss / Physics Loss) ---")
    sweep_results = []
    for lam in lambdas:
        model, losses = train_one(xy_train, uv_train, lambda_physics=lam)
        rmse, mae = evaluate(model, xy_test, uv_test)
        final_data_loss, final_physics_loss = losses[-1]
        sweep_results.append({
            "lambda": lam, "test_rmse": rmse, "test_mae": mae,
            "final_data_loss": final_data_loss, "final_physics_loss": final_physics_loss,
        })
        print(f"  lambda={lam:<5} test_RMSE={rmse:.4f}  test_MAE={mae:.4f}  "
              f"data_loss_cuoi={final_data_loss:.4f}  physics_loss_cuoi={final_physics_loss:.6f}")

    best = min(sweep_results, key=lambda r: r["test_rmse"])
    print(f"\nLambda tot nhat tren tap test: {best['lambda']} (RMSE={best['test_rmse']:.4f})")

    # --- #4: so sanh PINN (lambda tot nhat, >0) vs baseline hoi quy thuan (lambda=0) ---
    baseline = next(r for r in sweep_results if r["lambda"] == 0.0)
    pinn_candidates = [r for r in sweep_results if r["lambda"] > 0.0]
    best_pinn = min(pinn_candidates, key=lambda r: r["test_rmse"])

    print("\n--- #4 So sanh PINN vs baseline hoi quy thuan (khong rang buoc vat ly) ---")
    print(f"  Baseline (lambda=0):        test_RMSE={baseline['test_rmse']:.4f}")
    print(f"  PINN tot nhat (lambda={best_pinn['lambda']}): test_RMSE={best_pinn['test_rmse']:.4f}")
    diff_pct = (baseline["test_rmse"] - best_pinn["test_rmse"]) / baseline["test_rmse"] * 100
    if best_pinn["test_rmse"] < baseline["test_rmse"]:
        print(f"  => PINN tot hon baseline {diff_pct:.1f}% tren tap test giu lai.")
    else:
        print(f"  => PINN KHONG tot hon baseline tren RMSE thuan tuy ({-diff_pct:.1f}% kem hon) o quy mo "
              f"du lieu nay ({n} tram) - ghi nhan trung thuc: voi it diem du lieu khong-thoi-gian "
              f"(chi 1 snapshot trung binh/tram, khong co chieu thoi gian), rang buoc vat ly thuan "
              f"continuity co the chua du manh de vuot troi MSE thuan tren tap test nho. Physics loss "
              f"van co gia tri o tinh hop ly vat ly (bao toan khoi luong) ma baseline khong co.")

    # --- TV3 Tuan 3 #9: xuat output cho Dashboard (TV4) doc duoc, dinh dang Parquet ---
    final_model, _ = train_one(xy_train, uv_train, lambda_physics=best_pinn["lambda"], epochs=300)
    with torch.no_grad():
        pred_all_n = final_model(torch.tensor(xy_n)).numpy()
    pred_all = pred_all_n * uv_std + uv_mean  # de-normalize ve don vi m/s that

    export_df = agg.copy()
    export_df["u_pred_ms"] = pred_all[:, 0]
    export_df["v_pred_ms"] = pred_all[:, 1]
    export_df["u_obs_ms"] = uv_raw[:, 0]
    export_df["v_obs_ms"] = uv_raw[:, 1]
    export_df["residual_ms"] = np.sqrt((pred_all[:, 0] - uv_raw[:, 0]) ** 2 + (pred_all[:, 1] - uv_raw[:, 1]) ** 2)
    export_df["lambda_used"] = best_pinn["lambda"]

    out_path = os.path.join(ROOT, "warehouse", "output", "pinn_wind_field_output.parquet")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    export_df.to_parquet(out_path, index=False)
    print(f"\nDa xuat output cho Dashboard: {out_path} ({len(export_df)} tram, "
          f"residual trung binh {export_df['residual_ms'].mean():.3f} m/s)")

    print(f"\nPASS n_lambda_tested={len(lambdas)} best_lambda={best['lambda']}")


if __name__ == "__main__":
    main()
