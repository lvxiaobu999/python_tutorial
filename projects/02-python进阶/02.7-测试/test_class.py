import pytest
import numpy as np


def test_floats():
    assert (0.1 + 0.2) == pytest.approx(0.3)


def test_arrays():
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([0.9999, 2.0001, 3.0])
    # approx 默认 rel=1e-6 太严（数据差 1e-4），手动给绝对容差；给 1e-4 会压线失败
    assert a == pytest.approx(b, abs=1e-3)
