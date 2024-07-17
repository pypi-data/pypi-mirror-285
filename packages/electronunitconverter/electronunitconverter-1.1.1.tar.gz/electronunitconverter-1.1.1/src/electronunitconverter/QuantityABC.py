from abc import ABCMeta, abstractmethod

class Quantity(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'pprint') and 
                callable(subclass.pprint) and 
                hasattr(subclass, 'convert') and 
                callable(subclass.convert) or 
                NotImplemented)

    @abstractmethod
    def pprint(self) -> str:
        """Returns a str with the quantity in all available units"""
        raise NotImplementedError

    @abstractmethod
    def convert(self, unit : str) -> float:
        """Converts the quantity to the given unit"""
        raise NotImplementedError