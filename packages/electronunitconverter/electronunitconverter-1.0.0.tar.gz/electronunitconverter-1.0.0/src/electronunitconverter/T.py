from __future__ import annotations

from typing import Literal, SupportsFloat
from scipy.constants import physical_constants

from .QuantityABC import Quantity
from .errors import UnitError
from .Formatting import Formatter

TemperatureUnits = Literal["K", "GHz", "eV"]

class Temperature(Quantity):

    __slots__ = ["value_K"]

    __K_to_GHz = physical_constants["Boltzmann constant in Hz/K"][0] / 1e9
    __GHz_to_K = 1 / __K_to_GHz

    __K_to_eV = physical_constants["Boltzmann constant in eV/K"][0]
    __eV_to_K = 1 / __K_to_eV

    def __init__(self, value : SupportsFloat, unit : TemperatureUnits) -> None:
            
        if unit == "K":
            self.value_K = value
        elif unit == "GHz":
            self.value_K = value * self.__GHz_to_K
        elif unit == "eV":
            self.value_K = value * self.__eV_to_K
        else:
            raise UnitError("Invalid unit")

    def __repr__(self) -> str:
        return f"{self.value_K} K"
    
    def pprint(self) -> str:
        string = f"Temperature\n" + \
            Formatter(self.value_K, 'K').format() + "\n" + \
            Formatter(self.value_K * self.__K_to_GHz, 'GHz').format() + "\n" + \
            Formatter(self.value_K * self.__K_to_eV, 'eV').format() 
        return string
    
    def convert(self, unit : TemperatureUnits) -> float:
        if unit == "K":
            return self.value_K
        elif unit == "GHz":
            return self.value_K * self.__K_to_GHz
        elif unit == "eV":
            return self.value_K * self.__K_to_eV
        else:
            raise UnitError("Invalid unit")