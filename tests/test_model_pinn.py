"""
Smoke test cho 3 script PINN (docs/03 Tuần 1-2, TV3 #5/#6/#7) — chạy thật, không mock,
chỉ assert không lỗi + loss hội tụ (logic kiểm thử chi tiết đã nằm trong chính các script).

Chạy: pytest tests/test_model_pinn.py -v -m slow
(đánh dấu "slow" vì mỗi test huấn luyện thật vài chục-vài trăm epoch, vài giây/test)
"""
import os
import subprocess
import sys

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
pytestmark = pytest.mark.slow


def _run(script):
    result = subprocess.run(
        [sys.executable, os.path.join(ROOT, script)],
        capture_output=True, text=True, timeout=120, cwd=ROOT,
    )
    return result


def test_heat_equation_pinn_runs_and_converges():
    r = _run("model/train_demo.py")
    assert r.returncode == 0, f"Script loi:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


def test_navier_stokes_autograd_check():
    r = _run("model/navier_stokes_autograd_check.py")
    assert r.returncode == 0, f"Script loi:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


def test_clausius_clapeyron_physics_loss_on_real_data():
    r = _run("model/pinn_rh_from_dewpoint.py")
    assert r.returncode == 0, f"Script loi:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
