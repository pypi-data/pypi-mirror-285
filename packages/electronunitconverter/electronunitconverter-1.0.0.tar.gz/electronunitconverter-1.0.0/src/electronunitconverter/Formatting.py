from typing import Dict

class Formatter:

    def __init__(self, value : float, unit : str):
        self.value = value
        self.unit = unit

    def format(self) -> str:

        if self.unit == 'GHz':
            if self.value >=0.1:
                return f"{self.value:.1f} {self.unit}"
            elif self.value > 1e-4:
                return f"{self.value * 1e3:.1f} MHz"
            else:
                return f"{self.value:.1e} {self.unit}"
            
        elif self.unit == 'eV':
            if self.value >= 0.1:
                return f"{self.value:.1f} {self.unit}"
            elif self.value > 1e-4:
                return f"{self.value * 1e3:.1f} meV"
            elif self.value > 1e-7:
                return f"{self.value * 1e6:.1f} ueV"
            else:
                return f"{self.value:.1e} {self.unit}"
            
        else:
            if self.value >= 0.1:
                return f"{self.value:.1f} {self.unit}"
            elif self.value > 1e-4:
                return f"{self.value * 1e3:.1f} m{self.unit}"
            else:
                return f"{self.value:.1e} {self.unit}"