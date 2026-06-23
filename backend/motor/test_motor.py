# ============ PROMPT ============
# Pruebas unitarias con pytest para el motor EPiC: verifica cada tabla de verdad
# (NEG, AND, OR, XOR), la propagación en cadenas de nodos con premisas T/F/B/N,
# la convergencia a punto fijo y el método calcular_pasos que retorna el historial completo.
# ======== FIN DEL PROMPT ========

"""
test_motor.py — Tests del Motor de tablas EPiC.
Verifica que las tablas de verdad se aplican correctamente.
"""

import pytest
from compartido.modelos import Red, Nodo, Arista
from motor.algoritmos import obtener_motor, aplicar_operador, NEG_TABLE, AND_TABLE, OR_TABLE, XOR_TABLE


# ── Tests de las tablas de verdad ──────────────────────────────────────────────

class TestNEG:
    def test_neg_T_es_F(self):    assert NEG_TABLE["T"] == "F"
    def test_neg_F_es_T(self):    assert NEG_TABLE["F"] == "T"
    def test_neg_B_es_B(self):    assert NEG_TABLE["B"] == "B"
    def test_neg_N_es_N(self):    assert NEG_TABLE["N"] == "N"


class TestAND:
    def test_T_AND_T_es_T(self):  assert AND_TABLE[("T","T")] == "T"
    def test_T_AND_F_es_F(self):  assert AND_TABLE[("T","F")] == "F"
    def test_F_AND_T_es_F(self):  assert AND_TABLE[("F","T")] == "F"
    def test_F_AND_F_es_F(self):  assert AND_TABLE[("F","F")] == "F"
    def test_N_AND_T_es_N(self):  assert AND_TABLE[("N","T")] == "N"
    def test_T_AND_B_es_B(self):  assert AND_TABLE[("T","B")] == "B"


class TestOR:
    def test_T_OR_T_es_T(self):   assert OR_TABLE[("T","T")] == "T"
    def test_T_OR_F_es_T(self):   assert OR_TABLE[("T","F")] == "T"
    def test_F_OR_F_es_F(self):   assert OR_TABLE[("F","F")] == "F"
    def test_N_OR_T_es_T(self):   assert OR_TABLE[("N","T")] == "T"
    def test_N_OR_N_es_N(self):   assert OR_TABLE[("N","N")] == "N"
    def test_F_OR_B_es_B(self):   assert OR_TABLE[("F","B")] == "B"


class TestXOR:
    def test_T_XOR_T_es_F(self):  assert XOR_TABLE[("T","T")] == "F"  # exclusivo
    def test_T_XOR_F_es_T(self):  assert XOR_TABLE[("T","F")] == "T"
    def test_F_XOR_F_es_F(self):  assert XOR_TABLE[("F","F")] == "F"
    def test_B_XOR_T_es_B(self):  assert XOR_TABLE[("B","T")] == "B"  # contradicción se propaga
    def test_N_XOR_N_es_N(self):  assert XOR_TABLE[("N","N")] == "N"


# ── Tests de propagación ───────────────────────────────────────────────────────

def _red_cadena() -> Red:
    """P(T) → AND → NOT"""
    return Red(id="red-c", nodos=[
        Nodo(id="nodo-P", etiqueta="P", tipo="premisa", propiedades={"valor": "T"}),
        Nodo(id="nodo-A", etiqueta="A", tipo="AND",     propiedades={}),
        Nodo(id="nodo-N", etiqueta="¬A", tipo="NOT",    propiedades={}),
    ], aristas=[
        Arista(id="arista-1", id_origen="nodo-P", id_destino="nodo-A"),
        Arista(id="arista-2", id_origen="nodo-A", id_destino="nodo-N"),
    ])


class TestPropagacion:
    def test_premisa_T_se_propaga_por_AND(self):
        r = obtener_motor().calcular(_red_cadena())
        assert r.valores_nodos["nodo-A"] == "T"

    def test_NOT_invierte_T_a_F(self):
        r = obtener_motor().calcular(_red_cadena())
        assert r.valores_nodos["nodo-N"] == "F"

    def test_premisa_no_cambia(self):
        r = obtener_motor().calcular(_red_cadena())
        assert r.valores_nodos["nodo-P"] == "T"

    def test_converge(self):
        r = obtener_motor().calcular(_red_cadena())
        assert r.convergido is True

    def test_red_con_premisa_F_y_OR(self):
        red = Red(id="red-f", nodos=[
            Nodo(id="nodo-P1", etiqueta="P1", tipo="premisa", propiedades={"valor": "F"}),
            Nodo(id="nodo-P2", etiqueta="P2", tipo="premisa", propiedades={"valor": "T"}),
            Nodo(id="nodo-O",  etiqueta="O",  tipo="OR",      propiedades={}),
        ], aristas=[
            Arista(id="arista-1", id_origen="nodo-P1", id_destino="nodo-O"),
            Arista(id="arista-2", id_origen="nodo-P2", id_destino="nodo-O"),
        ])
        r = obtener_motor().calcular(red)
        assert r.valores_nodos["nodo-O"] == "T"  # F OR T = T

    def test_contradiccion_se_propaga(self):
        red = Red(id="red-b", nodos=[
            Nodo(id="nodo-P", etiqueta="P", tipo="premisa", propiedades={"valor": "B"}),
            Nodo(id="nodo-O", etiqueta="O", tipo="OR",      propiedades={}),
        ], aristas=[
            Arista(id="arista-1", id_origen="nodo-P", id_destino="nodo-O"),
        ])
        r = obtener_motor().calcular(red)
        assert r.valores_nodos["nodo-O"] == "B"

    def test_sin_evidencia_en_cadena(self):
        """Si la premisa es N, los operadores quedan en N."""
        red = Red(id="red-n", nodos=[
            Nodo(id="nodo-P", etiqueta="P", tipo="premisa", propiedades={"valor": "N"}),
            Nodo(id="nodo-A", etiqueta="A", tipo="AND",     propiedades={}),
        ], aristas=[
            Arista(id="arista-1", id_origen="nodo-P", id_destino="nodo-A"),
        ])
        r = obtener_motor().calcular(red)
        assert r.valores_nodos["nodo-A"] == "N"


class TestPasos:
    def test_calcular_pasos_devuelve_lista(self):
        pasos = obtener_motor().calcular_pasos(_red_cadena())
        assert len(pasos) >= 1

    def test_ultimo_paso_converge(self):
        pasos = obtener_motor().calcular_pasos(_red_cadena())
        assert pasos[-1].convergido is True

    def test_todos_los_pasos_tienen_todos_los_nodos(self):
        pasos = obtener_motor().calcular_pasos(_red_cadena())
        for p in pasos:
            assert set(p.valores_nodos.keys()) == {"nodo-P", "nodo-A", "nodo-N"}
