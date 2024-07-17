from __future__ import annotations

from typing import Literal, SupportsFloat
from scipy.constants import physical_constants

from .QuantityABC import Quantity
from .errors import UnitError
from .Formatting import Formatter

VoltageUnits = Literal["GHz", "eV"]

class Voltage(Quantity):

    __slots__ = ["value_eV"]

    __eV_to_GHz = 1e-9 / physical_constants["Planck constant in eV/Hz"][0]
    __GHz_to_eV = 1 / __eV_to_GHz

    def __init__(self, value : SupportsFloat, unit : VoltageUnits) -> None:
        
        if unit == "eV":
            self.value_eV = value
        elif unit == "GHz":
            self.value_eV = value * self.__GHz_to_eV
        else:
            raise UnitError("Invalid unit")

    def __repr__(self) -> str:
        return f"{self.value_eV} eV"
    
    def pprint(self) -> str:
        string = f"Voltage\n" + \
            Formatter(self.value_eV, 'eV').format() + "\n" + \
            Formatter(self.value_eV * self.__eV_to_GHz, 'GHz').format()
        return string
    
    def convert(self, unit : VoltageUnits) -> float:
        if unit == "eV":
            return self.value_eV
        elif unit == "GHz":
            return self.value_eV * self.__eV_to_GHz
        else:
            raise UnitError("Invalid unit")
        