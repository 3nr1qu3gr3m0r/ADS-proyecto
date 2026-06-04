"""
i_motor_calculo.py — Interface IMotorCalculo (SOLID I y D)
"""

from abc import ABC, abstractmethod
from .modelos import Red, ResultadoPropagacion


class IMotorCalculo(ABC):
    @abstractmethod
    def calcular(self, red: Red) -> ResultadoPropagacion:
        pass