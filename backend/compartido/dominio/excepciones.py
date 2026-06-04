"""
excepciones.py — Excepciones personalizadas del sistema
"""


class RedInvalidaError(Exception):
    pass


class ConvergenciaError(Exception):
    pass


class MatrizSingularError(Exception):
    pass