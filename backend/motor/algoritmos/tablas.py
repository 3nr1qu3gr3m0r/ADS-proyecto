"""
Tablas evidenciales de los conectivos de EPiC.

Cada tabla es un diccionario:  (input...) -> output
Los valores son frozensets de {0, 1} tal como define el artículo.
"""

from motor.algoritmos.constantes import N, T, F, B


# ──────────────────────────────────────────────
# Negación: ¬x  (invierte polaridad)
# ──────────────────────────────────────────────
NEG_TABLE = {
    N: N,
    T: F,
    F: T,
    B: B,
}

# ──────────────────────────────────────────────
# Implicación: x → y  ≡  ¬x ∨ y
# ──────────────────────────────────────────────
IMP_TABLE = {
    (N, N): N, (N, T): T, (N, F): N, (N, B): T,
    (T, N): N, (T, T): T, (T, F): F, (T, B): B,
    (F, N): T, (F, T): T, (F, F): T, (F, B): T,
    (B, N): T, (B, T): T, (B, F): B, (B, B): B,
}

# ──────────────────────────────────────────────
# Conjunción: x ∧ y
#   1 ∈ (x∧y)  ssi  1∈x  y  1∈y
#   0 ∈ (x∧y)  ssi  0∈x  o  0∈y
# ──────────────────────────────────────────────
AND_TABLE = {
    (N, N): N, (N, T): N, (N, F): F, (N, B): F,
    (T, N): N, (T, T): T, (T, F): F, (T, B): B,
    (F, N): F, (F, T): F, (F, F): F, (F, B): F,
    (B, N): F, (B, T): B, (B, F): F, (B, B): B,
}

# ──────────────────────────────────────────────
# Disyunción: x ∨ y
#   1 ∈ (x∨y)  ssi  1∈x  o  1∈y
#   0 ∈ (x∨y)  ssi  0∈x  y  0∈y
# ──────────────────────────────────────────────
OR_TABLE = {
    (N, N): N, (N, T): T, (N, F): N, (N, B): T,
    (T, N): T, (T, T): T, (T, F): T, (T, B): T,
    (F, N): N, (F, T): T, (F, F): F, (F, B): B,
    (B, N): T, (B, T): T, (B, F): B, (B, B): B,
}
