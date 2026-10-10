#!/usr/bin/env python3
"""
Ví dụ PINN tối thiểu chuẩn: phương trình nhiệt 1D (docs/03 Tuần 1, TV3 #5).
    u_t = alpha * u_xx,  x trong [0,1], t trong [0,1]
    Dieu kien bien: u(0,t)=u(1,t)=0 ;  Dieu kien dau: u(x,0)=sin(pi*x)
    Nghiem giai tich de doi chieu: u(x,t) = exp(-alpha*pi^2*t) * sin(pi*x)

Day la vi du kinh dien (Raissi et al. 2019) de xac nhan framework PINN (PyTorch +
autograd) hoat dong dung truoc khi ap dung vao bai toan khi tuong that (xem
model/pinn_rh_from_dewpoint.py va model/navier_stokes_autograd_check.py).

Chay: python3 model/train_demo.py
"""
import math

import torch
import torch.nn as nn

torch.manual_seed(0)
ALPHA = 1.0


class PINN(nn.Module):
    def __init__(self, hidden=32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(2, hidden), nn.Tanh(),
            nn.Linear(hidden, hidden), nn.Tanh(),
            nn.Linear(hidden, 1),
        )

    def forward(self, x, t):
        return self.net(torch.cat([x, t], dim=1))


def physics_residual(model, x, t):
    x = x.clone().requires_grad_(True)
    t = t.clone().requires_grad_(True)
    u = model(x, t)
    u_t = torch.autograd.grad(u, t, grad_outputs=torch.ones_like(u), create_graph=True)[0]
    u_x = torch.autograd.grad(u, x, grad_outputs=torch.ones_like(u), create_graph=True)[0]
    u_xx = torch.autograd.grad(u_x, x, grad_outputs=torch.ones_like(u_x), create_graph=True)[0]
    return u_t - ALPHA * u_xx


def main():
    model = PINN()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    n_collocation = 200
    x_f = torch.rand(n_collocation, 1)
    t_f = torch.rand(n_collocation, 1)

    n_ic = 50
    x_ic = torch.rand(n_ic, 1)
    t_ic = torch.zeros(n_ic, 1)
    u_ic_true = torch.sin(math.pi * x_ic)

    n_bc = 50
    t_bc = torch.rand(n_bc, 1)
    x_bc0 = torch.zeros(n_bc, 1)
    x_bc1 = torch.ones(n_bc, 1)

    print("Bat dau huan luyen PINN 1D heat equation (100 epoch)...")
    losses = []
    for epoch in range(100):
        optimizer.zero_grad()
        residual = physics_residual(model, x_f, t_f)
        loss_physics = (residual ** 2).mean()
        loss_ic = ((model(x_ic, t_ic) - u_ic_true) ** 2).mean()
        loss_bc = (model(x_bc0, t_bc) ** 2).mean() + (model(x_bc1, t_bc) ** 2).mean()
        loss = loss_physics + loss_ic + loss_bc

        if torch.isnan(loss) or torch.isinf(loss):
            raise RuntimeError(f"Loss NaN/Inf o epoch {epoch} -- PINN khong hoi tu")

        loss.backward()
        optimizer.step()
        losses.append(loss.item())
        if epoch % 20 == 0:
            print(f"  epoch {epoch:3d}: loss={loss.item():.6f} "
                  f"(physics={loss_physics.item():.6f}, ic={loss_ic.item():.6f}, bc={loss_bc.item():.6f})")

    assert losses[-1] < losses[0], "Loss khong giam -- huan luyen that bai"
    print(f"\nKiem thu: loss giam tu {losses[0]:.6f} -> {losses[-1]:.6f}. Khong NaN/Inf. PASS.")

    # Doi chieu voi nghiem giai tich u(x,t) = exp(-alpha*pi^2*t)*sin(pi*x)
    with torch.no_grad():
        x_test = torch.tensor([[0.5]])
        t_test = torch.tensor([[0.1]])
        u_pred = model(x_test, t_test).item()
        u_exact = math.exp(-ALPHA * math.pi**2 * 0.1) * math.sin(math.pi * 0.5)
        print(f"\nDoi chieu nghiem giai tich tai x=0.5, t=0.1: du doan={u_pred:.4f}, "
              f"giai tich={u_exact:.4f}, sai lech={abs(u_pred - u_exact):.4f}")


if __name__ == "__main__":
    main()
