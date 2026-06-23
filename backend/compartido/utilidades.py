# ============ PROMPT ============
# Implementa funciones auxiliares puras y sin dependencias del dominio EPiC:
# generación de IDs únicos con prefijo UUID, formateo y redondeo numérico
# a 4 decimales, y clamping de valores flotantes al rango [0, 1].
# ======== FIN DEL PROMPT ========

"""
utilidades.py — Funciones de utilidad compartidas, sin estado y sin
dependencias de ningún otro módulo del sistema.
"""

import uuid


def generar_id(prefijo: str = "id") -> str:
    return f"{prefijo}-{uuid.uuid4().hex[:8]}"


def formatear_resultado(valor: float) -> str:
    return f"{valor:.4f}"


def redondear(valor: float, decimales: int = 4) -> float:
    factor = 10 ** decimales
    return round(valor * factor) / factor


def clamp(valor: float, minimo: float = 0.0, maximo: float = 1.0) -> float:
    return max(minimo, min(maximo, valor))
