"""
contratos.py — Interfaces, enumeraciones, eventos y excepciones compartidas.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from compartido.modelos import Red, ResultadoPropagacion

TIPOS_OPERADOR = {"AND", "OR", "XOR", "NOT", "IMP", "MT"}
VALORES_BELNAP = {"T", "F", "B", "N"}


class FaseSimulacion(str, Enum):
    INACTIVO   = "inactivo"
    CORRIENDO  = "corriendo"
    PAUSADO    = "pausado"
    COMPLETADO = "completado"
    ERROR      = "error"


class IMotorCalculo(ABC):
    """Contrato mínimo: dada una red, calcula su resultado final."""

    @abstractmethod
    def calcular(self, red: Red) -> ResultadoPropagacion:
        ...


class IMotorCalculoIterativo(IMotorCalculo):
    """
    Extiende IMotorCalculo para exponer el detalle de cada iteración del
    algoritmo de punto fijo sobre las tablas de verdad EPiC.
    El Simulador depende de esta interfaz para mostrar la propagación paso a paso.
    """

    @abstractmethod
    def calcular_pasos(self, red: Red) -> list[ResultadoPropagacion]:
        ...


class ISimulacion(ABC):
    @abstractmethod
    def iniciar(self, red: Red) -> str:
        ...

    @abstractmethod
    def pausar(self) -> None:
        ...

    @abstractmethod
    def reanudar(self) -> None:
        ...

    @abstractmethod
    def paso(self) -> None:
        ...


@dataclass
class RedActualizada:
    tipo: str = "RedActualizada"
    redId: str = ""


@dataclass
class SimulacionIniciada:
    tipo: str = "SimulacionIniciada"
    redId: str = ""


@dataclass
class ErrorCalculo:
    tipo: str = "ErrorCalculo"
    mensaje: str = ""


class RedInvalidaError(Exception):
    pass


class ConvergenciaError(Exception):
    pass
