import numpy as np

from electronunitconverter import Temperature, Voltage

def test_meV_to_GHz():

    eV_to_GHz = Voltage._Voltage__eV_to_GHz

    K_to_eV = Temperature._Temperature__K_to_eV
    K_to_GHz = Temperature._Temperature__K_to_GHz

    assert np.isclose(eV_to_GHz, float(K_to_GHz / K_to_eV))