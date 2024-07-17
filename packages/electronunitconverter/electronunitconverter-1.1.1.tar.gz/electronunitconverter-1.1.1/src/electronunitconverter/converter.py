from __future__ import annotations

from typing import Literal, SupportsFloat, Tuple, Union
import re

from .B import MagneticField
from .T import Temperature
from .V import Voltage

from .QuantityABC import Quantity
from .errors import QuantityError

class UnitConverter:

    def __init__(self, input_string : str) -> None:
        self.input_string = input_string
        self.quantity = self._parse_input()

    def _parse_input(self) -> Quantity:

        match = re.match(r"([a-zA-Z]+)\s*=?\s*([0-9.-]+)\s*([a-zA-Z]+)", self.input_string)
        if match is None:
            raise ValueError("Invalid input string")
        quantity, value, unit = match.groups()

        quantity = quantity.upper()

        if unit.startswith("m"):
            value = float(value) / 1000
            unit = unit[1:]
        elif unit.startswith("u"):
            value = float(value) / 1e6
            unit = unit[1:]
        elif unit.startswith("n"):
            value = float(value) / 1e9
            unit = unit[1:]
        elif unit == "MHz":
            value = float(value) / 1e3
            unit = "GHz"

        if quantity == "B":
            return MagneticField(float(value), unit)
        elif quantity == "V":
            return Voltage(float(value), unit)
        elif quantity == "T":
            return Temperature(float(value), unit)
        else:
            raise QuantityError("Invalid quantity")
        
    def parse(self) -> Quantity:
        return self.quantity
    
    def pprint(self) -> str:
        return self.quantity.pprint()
    
    def convert(self, unit : str) -> float:
        return self.quantity.convert(unit)
    
