#!/usr/bin/env python3
"""
Kiểm tra autograd cho ràng buộc Navier-Stokes 2D rút gọn (docs/03 Tuần 2, TV3 #7),
dùng để làm mịn trường gió (u,v) nội suy từ lưới ERA5 (docs/06 mục 4b).

Phương trình rút gọn dùng làm ràng buộc vật lý (bảo toàn khối lượng, incompressible,
không xét nhớt/Coriolis để giữ tối giản — đúng phạm vi "tối thiểu, khả thi" đã cam kết
trong report/main.tex Mục 3.4):
    continuity:  du/dx + dv/dy = 0   (bao toan khoi luong 2D)

Chạy: python3 model/navier_stokes_autograd_check.py
"""
import torch
import torch.nn as nn

torch.manual_seed(0)


class WindFieldNet(nn.Module):
    """Du doan (u,v) tai vi tri (x,y) -- dung lam mang noi suy min hon luoi ERA5 goc."""
    def __init__(self, hidden=32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(2, hidden), nn.Tanh(),
            nn.Linear(hidden, hidden), nn.Tanh(),
            nn.Linear(hidden, 2),  # output: u, v
        )

    def forward(self, xy):
        return self.net(xy)


def continuity_residual(model, xy):
    xy = xy.clone().requires_grad_(True)
    uv = model(xy)
    u, v = uv[:, 0:1], uv[:, 1:2]

    du = torch.autograd.grad(u, xy, grad_outputs=torch.ones_like(u), create_graph=True)[0]
    dv = torch.autograd.grad(v, xy, grad_outputs=torch.ones_like(v), create_graph=True)[0]
    du_dx = du[:, 0:1]
    dv_dy = dv[:, 1:2]
    return du_dx + dv_dy  # continuity residual, muon ep ve 0


def main():
    model = WindFieldNet()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    xy = torch.rand(100, 2, requires_grad=False)

    print("Kiem tra gradient flow qua autograd...")
    residual = continuity_residual(model, xy)
    loss = (residual ** 2).mean()
    loss.backward()

    # Luu y toan hoc quan trong: bias cua lop OUTPUT cuoi cung (net.4.bias) se luon co
    # grad=None voi loss nay -- vi residual (du/dx + dv/dy) la dao ham, bat bien voi hang
    # so cong them vao u,v (d(const)/dx = 0). Day la hanh vi autograd DUNG, khong phai loi.
    # Nen chi kiem tra gradient tren cac tham so WEIGHT (quyet dinh cau truc dao ham).
    weight_params = {n: p for n, p in model.named_parameters() if "weight" in n}
    grads_ok = all(p.grad is not None for p in weight_params.values())
    any_nonzero = any((p.grad.abs().sum() > 0).item() for p in weight_params.values() if p.grad is not None)
    bias_final_is_none = model.net[4].bias.grad is None
    print(f"  loss.backward() chay thanh cong: True")
    print(f"  Tat ca tham so WEIGHT co gradient != None: {grads_ok}")
    print(f"  Co it nhat 1 gradient khac 0: {any_nonzero}")
    print(f"  net.4.bias grad=None (dung ve mat toan hoc, residual bat bien voi hang so cong them): {bias_final_is_none}")
    assert grads_ok, "LOI: co tham so WEIGHT khong nhan duoc gradient (gradient = None)"
    assert any_nonzero, "LOI: tat ca gradient = 0, khong hoc duoc gi"

    print("\nHuan luyen rang buoc continuity (bao toan khoi luong) qua 50 epoch...")
    losses = []
    for epoch in range(50):
        optimizer.zero_grad()
        residual = continuity_residual(model, xy)
        loss = (residual ** 2).mean()
        loss.backward()
        optimizer.step()
        losses.append(loss.item())
        if epoch % 10 == 0:
            print(f"  epoch {epoch:2d}: continuity_loss={loss.item():.6f}")

    assert losses[-1] < losses[0], "Loss khong giam"
    print(f"\nKiem thu: loss giam {losses[0]:.6f} -> {losses[-1]:.6f}. PASS -- "
          f"autograd tinh dung gradient qua 2 lan dao ham (du/dx, dv/dy).")


if __name__ == "__main__":
    main()
