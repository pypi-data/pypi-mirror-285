import pytest
import numpy as np

from electronunitconverter import Temperature

from scipy.constants import physical_constants

K_to_GHz = physical_constants["Boltzmann constant in Hz/K"][0] / 1e9
K_to_meV = physical_constants["Boltzmann constant in eV/K"][0] * 1e3

@pytest.mark.parametrize('T_K', [np.random.rand() for _ in range(100)])
def test_GHz_to_K(T_K):
    
    T_quantity = Temperature(T_K, "K")

    assert np.isclose(T_quantity.convert("GHz"), T_K * K_to_GHz)

@pytest.mark.parametrize('T_GHz', [np.random.rand() for _ in range(100)])
def test_K_to_GHz(T_GHz):
    
    T_quantity = Temperature(T_GHz, "GHz")

    assert np.isclose(T_quantity.convert("K"), T_GHz / K_to_GHz)