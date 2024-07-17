import pytest
import numpy as np

from electronunitconverter import MagneticField

from scipy.constants import physical_constants

T_to_GHz = physical_constants["Bohr magneton in Hz/T"][0] / 1e9

@pytest.mark.parametrize('B_T', [np.random.rand() for _ in range(100)])
def test_GHz_to_T(B_T):
    
    B_quantity = MagneticField(B_T, "T")

    assert np.isclose(B_quantity.convert("GHz"), B_T * T_to_GHz)

@pytest.mark.parametrize('B_GHz', [np.random.rand() for _ in range(100)])
def test_T_to_GHz(B_GHz):
    
    B_quantity = MagneticField(B_GHz, "GHz")

    assert np.isclose(B_quantity.convert("T"), B_GHz / T_to_GHz)
