"""
utilidades.py — Funciones de utilidad compartidas
"""

import uuid


def generar_id(prefix: str = 'id') -> str:
    return f'{prefix}-{uuid.uuid4().hex[:8]}'


def formatear_resultado(valor: float) -> str:
    return f'{valor:.4f}'


def redondear(valor: float, decimales: int = 4) -> float:
    factor = 10 ** decimales
    return round(valor * factor) / factor