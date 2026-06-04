"""
enumeraciones.py — Enumeraciones del sistema (espejo de tipos.ts del README)
"""

from enum import Enum


class TipoNodo(str, Enum):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class FaseSimulacion(str, Enum):
    INACTIVO = "inactivo"
    CORRIENDO = "corriendo"
    PAUSADO = "pausado"
    COMPLETADO = "completado"
    ERROR = "error"