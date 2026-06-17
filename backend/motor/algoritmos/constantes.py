# Dominio evidencial V = {N, T, F, B}
# Representados como frozensets de {0, 1} (igual que en el artículo)

N = frozenset()        # Sin evidencia
T = frozenset({1})     # Evidencia positiva
F = frozenset({0})     # Evidencia negativa
B = frozenset({0, 1})  # Ambas (inconsistencia evidencial)

# Mapeados a strings legibles
VALUE_NAMES = {N: "N", T: "T", F: "F", B: "B"}
NAME_TO_VALUE = {"N": N, "T": T, "F": F, "B": B}

# Orden evidencial: x <= y  ssi  x ⊆ y
def evidential_leq(x, y):
    return x <= y

def future_admissible(x):
    """Valores alcanzables desde x (upper set generado por x)."""
    return {v for v in (N, T, F, B) if evidential_leq(x, v)}

def min_surviving(s: set):
    """Elementos minimales de s bajo el orden evidencial."""
    return {x for x in s if not any(y < x for y in s)}
