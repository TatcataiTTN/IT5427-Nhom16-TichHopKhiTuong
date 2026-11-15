#!/usr/bin/env python3
"""Ve duong cong huan luyen PINN that (Data Loss + Physics Loss theo epoch, lambda=0 vs 0,1) cho slide.
Chay lai huan luyen that (khong doc file cache) de dam bao hinh luon khop code hien tai.
Chay: python3 warehouse/plot_pinn_training.py   (can torch: python3 mac dinh, khong phai homebrew)
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "model"))
import pinn_wind_field_v2 as m  # noqa: E402

OUT = os.path.join(ROOT, "slides", "images", "pinn_training_curve.png")

plt.rcParams.update({
    "font.family": "serif", "font.size": 10, "axes.titlesize": 11,
    "axes.labelsize": 10, "legend.fontsize": 9, "xtick.labelsize": 9, "ytick.labelsize": 9,
})

HUST_NAVY = "#17375E"
HUST_RED = "#C0443F"


def main():
    xy_raw, uv_raw, agg = m.load_real_wind_data()
    n = len(xy_raw)
    xy_mean, xy_std = xy_raw.mean(0), xy_raw.std(0)
    uv_mean, uv_std = uv_raw.mean(0), uv_raw.std(0)
    xy_n = m.normalize(xy_raw, xy_mean, xy_std)
    uv_n = m.normalize(uv_raw, uv_mean, uv_std)

    import numpy as np
    rng = np.random.RandomState(42)
    idx = rng.permutation(n)
    n_test = max(5, int(n * 0.2))
    test_idx, train_idx = idx[:n_test], idx[n_test:]
    xy_train, uv_train = xy_n[train_idx], uv_n[train_idx]
    xy_test, uv_test = xy_n[test_idx], uv_n[test_idx]
    print(f"n={n} train={len(train_idx)} test={len(test_idx)}")

    _, losses0 = m.train_one(xy_train, uv_train, lambda_physics=0.0, epochs=300)
    model1, losses1 = m.train_one(xy_train, uv_train, lambda_physics=0.1, epochs=300)
    rmse0, _ = m.evaluate(_, xy_test, uv_test)
    rmse1, _ = m.evaluate(model1, xy_test, uv_test)
    print(f"RMSE test: lambda=0 -> {rmse0:.4f} | lambda=0.1 -> {rmse1:.4f}")

    data0 = [d for d, p in losses0]
    data1 = [d for d, p in losses1]
    phys1 = [p for d, p in losses1]
    epochs = list(range(1, len(losses0) + 1))

    fig, axes = plt.subplots(1, 2, figsize=(7.6, 2.95), constrained_layout=True)

    ax = axes[0]
    ax.plot(epochs, data0, color="#8A8F98", lw=1.6, label=r"Data Loss, $\lambda=0$ (baseline)")
    ax.plot(epochs, data1, color=HUST_NAVY, lw=1.8, label=r"Data Loss, $\lambda=0{,}1$ (PINN)")
    ax.set_yscale("log")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Data Loss (MSE, đã chuẩn hoá)")
    ax.set_title("(a) Data Loss hội tụ", loc="left", fontweight="bold")
    ax.legend(frameon=False, loc="upper right")
    ax.grid(alpha=0.25, lw=0.5)

    ax2 = axes[1]
    ax2.plot(epochs, phys1, color=HUST_RED, lw=1.8)
    ax2.set_yscale("log")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel(r"Physics Loss  $\overline{(\partial u/\partial x+\partial v/\partial y)^2}$")
    ax2.set_title("(b) Dư liên tục tăng rồi chững lại", loc="left", fontweight="bold")
    ax2.grid(alpha=0.25, lw=0.5)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, dpi=200)
    print(f"Da luu: {OUT}")
    print(f"Data loss cuoi: lambda=0 -> {data0[-1]:.4f} | lambda=0,1 -> {data1[-1]:.4f}")
    print(f"Physics loss cuoi (lambda=0,1): {phys1[-1]:.6f} (dau: {phys1[0]:.6f})")


if __name__ == "__main__":
    main()
