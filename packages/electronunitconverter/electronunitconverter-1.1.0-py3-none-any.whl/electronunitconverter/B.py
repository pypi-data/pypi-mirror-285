from __future__ import annotations

from typing import Literal, SupportsFloat
from scipy.constants import physical_constants

from .QuantityABC import Quantity
from .errors import UnitError
from .Formatting import Formatter

MagneticUnits = Literal["T", "GHz"]

class MagneticField(Quantity):

    __slots__ = ["value_T"]

    __T_to_GHz = physical_constants["Bohr magneton in Hz/T"][0] / 1e9
    __GHz_to_T = 1 / __T_to_GHz

    def __init__(self, value : SupportsFloat, unit : MagneticUnits) -> None:
        
        if unit == "T":
            self.value_T = value
        elif unit == "GHz":
            self.value_T = value * self.__GHz_to_T
        else:
            raise UnitError("Invalid unit")

    def __repr__(self) -> str:
        return f"{self.value_T} T"
    
    def pprint(self) -> str:
        string = f"Magnetic Field\n"+                            \
        Formatter(self.value_T, 'T').format() + "\n"+            \
        Formatter(self.value_T * self.__T_to_GHz, 'GHz').format()
        return string
    
    def convert(self, unit : MagneticUnits) -> float:
        if unit == "T":
            return self.value_T
        elif unit == "GHz":
            return self.value_T * self.__T_to_GHz
        else:
            raise UnitError("Invalid unit")