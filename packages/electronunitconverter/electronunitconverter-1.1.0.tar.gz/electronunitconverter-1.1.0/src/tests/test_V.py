import pytest
import numpy as np

from electronunitconverter import Voltage

from scipy.constants import physical_constants

eV_to_GHz = 1e-9 / physical_constants["Planck constant in eV/Hz"][0]

@pytest.mark.parametrize('V_eV', [np.random.rand() for _ in range(100)])
def test_GHz_to_meV(V_eV):
    
    V_quantity = Voltage(V_eV, "eV")

    assert np.isclose(V_quantity.convert("GHz"), V_eV * eV_to_GHz)

@pytest.mark.parametrize('V_GHz', [np.random.rand() for _ in range(100)])
def test_meV_to_GHz(V_GHz):
    
    V_quantity = Voltage(V_GHz, "GHz")

    assert np.isclose(V_quantity.convert("eV"), V_GHz / eV_to_GHz)