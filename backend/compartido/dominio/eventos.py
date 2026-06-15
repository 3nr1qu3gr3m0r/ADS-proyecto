"""
eventos.py — Eventos del sistema entre componentes
"""

from dataclasses import dataclass


@dataclass
class RedActualizada:
    tipo: str = 'RedActualizada'
    redId: str = ''


@dataclass
class SimulacionIniciada:
    tipo: str = 'SimulacionIniciada'
    redId: str = ''


@dataclass
class ErrorCalculo:
    tipo: str = 'ErrorCalculo'
    mensaje: str = ''