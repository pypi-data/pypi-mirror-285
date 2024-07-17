import numpy as np

from electronunitconverter import (
    Temperature,
    Voltage,
    MagneticField,
    UnitConverter
)

input_templates = [
        '{Q}=1 {U}',
        '{Q}=1{U}',
        '{Q}1{U}',
        '{Q} 1 {U}',
    ]

def test_B():
    B = MagneticField(1, "T")

    input_strings = [ template.format(Q="B", U="T") for template in input_templates ]

    for input_string in input_strings:
        converter = UnitConverter(input_string)
        assert isinstance(B, MagneticField)
        assert np.isclose(B.convert("T"), converter.convert("T"))

def test_T():

    T = Temperature(1, "K")

    input_strings = [ template.format(Q="T", U="K") for template in input_templates ]

    for input_string in input_strings:
        converter = UnitConverter(input_string)
        assert isinstance(T, Temperature)
        assert np.isclose(T.convert("K"), converter.convert("K"))

def test_V():

    V = Voltage(1, "eV")

    input_strings = [ template.format(Q="V", U="eV") for template in input_templates ]

    for input_string in input_strings:
        converter = UnitConverter(input_string)
        assert isinstance(V, Voltage)
        assert np.isclose(V.convert("eV"), converter.convert("eV"))


def test_milli():
    B = MagneticField(1e-3, "T")

    input_strings = [ template.format(Q="B", U="mT") for template in input_templates ]

    for input_string in input_strings:
        converter = UnitConverter(input_string)
        assert isinstance(B, MagneticField)
        assert np.isclose(B.convert("T"), converter.convert("T"))

def test_MHz():
    B = MagneticField(1e-3, "GHz")

    input_strings = [ template.format(Q="B", U="MHz") for template in input_templates ]

    for input_string in input_strings:
        converter = UnitConverter(input_string)
        assert isinstance(B, MagneticField)
        assert np.isclose(B.convert("T"), converter.convert("T"))