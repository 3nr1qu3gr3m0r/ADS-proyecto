"""
i_simulacion.py — Interface ISimulacion (SOLID I y D)
"""

from abc import ABC, abstractmethod
from .modelos import Red


class ISimulacion(ABC):
    @abstractmethod
    def iniciar(self, red: Red) -> str:
        pass

    @abstractmethod
    def pausar(self) -> None:
        pass

    @abstractmethod
    def reanudar(self) -> None:
        pass

    @abstractmethod
    def paso(self) -> None:
        pass