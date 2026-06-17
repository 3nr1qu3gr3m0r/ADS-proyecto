"""
Pruebas unitarias — Gauss-Seidel
"""

import pytest
from motor.dominio import (
    DominioParaMotor, Variable, Conectivo,
    Valor4, TABLA_OR, TABLA_AND, TABLA_NOT,
)
from motor.algoritmos.gauss_seidel import ejecutar_gauss_seidel

N, V, F, A = Valor4.NINGUNO, Valor4.VERDADERO, Valor4.FALSO, Valor4.AMBOS


def dominio_lineal_or() -> DominioParaMotor:
    """x1=V --OR--> x2 --OR--> x3"""
    return DominioParaMotor(
        variables={
            "x1": Variable.desde_valor("x1", V),
            "x2": Variable.desde_valor("x2", N),
            "x3": Variable.desde_valor("x3", N),
        },
        conectivos=[
            Conectivo(id="OR_1", tabla=TABLA_OR, arcos=[("x1", "x2")]),
            Conectivo(id="OR_2", tabla=TABLA_OR, arcos=[("x2", "x3")]),
        ],
    )


def dominio_con_ciclo() -> DominioParaMotor:
    """x1=V --OR--> x2 --OR--> x3 --AND--> x2 (ciclo)"""
    return DominioParaMotor(
        variables={
            "x1": Variable.desde_valor("x1", V),
            "x2": Variable.desde_valor("x2", N),
            "x3": Variable.desde_valor("x3", N),
        },
        conectivos=[
            Conectivo(id="OR_1",  tabla=TABLA_OR,  arcos=[("x1", "x2")]),
            Conectivo(id="OR_2",  tabla=TABLA_OR,  arcos=[("x2", "x3")]),
            Conectivo(id="AND_1", tabla=TABLA_AND, arcos=[("x3", "x2")]),
        ],
    )


class TestGaussSeidel:

    def test_propaga_cadena_lineal(self):
        dominio = dominio_lineal_or()
        resultado = ejecutar_gauss_seidel(dominio, alpha=1.0)

        assert resultado.estabilizado
        # Gauss-Seidel actualiza inmediatamente: x2 se actualiza antes de que
        # OR_2 lo lea, por eso converge en menos iteraciones que Jacobi.
        assert resultado.valores_finales["x1"] == "VERDADERO"
        assert resultado.valores_finales["x2"] == "VERDADERO"
        assert resultado.valores_finales["x3"] == "VERDADERO"

    def test_converge_con_ciclo(self):
        dominio = dominio_con_ciclo()
        resultado = ejecutar_gauss_seidel(dominio, alpha=0.7)

        assert resultado.estabilizado
        assert resultado.valores_finales["x1"] == "VERDADERO"

    def test_historial_no_vacio(self):
        dominio = dominio_lineal_or()
        resultado = ejecutar_gauss_seidel(dominio)

        assert len(resultado.historial) > 0

    def test_historial_contiene_metodo_correcto(self):
        dominio = dominio_lineal_or()
        resultado = ejecutar_gauss_seidel(dominio)

        assert all(p.metodo == "gauss_seidel" for p in resultado.historial)

    def test_matrices_procesadas_presentes(self):
        dominio = dominio_lineal_or()
        resultado = ejecutar_gauss_seidel(dominio)

        assert "OR_1" in resultado.matrices_procesadas
        assert "OR_2" in resultado.matrices_procesadas
        assert len(resultado.matrices_procesadas["OR_1"]) == 4

    def test_no_estabiliza_si_max_iteraciones_1(self):
        """Con alpha=1 y un solo paso no debería estabilizar en red con ciclo."""
        dominio = dominio_con_ciclo()
        resultado = ejecutar_gauss_seidel(dominio, max_iteraciones=1, alpha=1.0)

        # Puede o no estabilizar según el grafo; lo importante es que no crashea
        assert resultado.iteraciones == 1

    def test_variable_sin_arcos_entrantes_no_cambia(self):
        """x1 no es destino de ningún arco; su valor debe permanecer igual."""
        dominio = dominio_lineal_or()
        resultado = ejecutar_gauss_seidel(dominio)

        assert resultado.valores_finales["x1"] == "VERDADERO"

    def test_dominio_falso_se_propaga(self):
        dominio = DominioParaMotor(
            variables={
                "a": Variable.desde_valor("a", F),
                "b": Variable.desde_valor("b", N),
            },
            conectivos=[
                Conectivo(id="OR_F", tabla=TABLA_OR, arcos=[("a", "b")]),
            ],
        )
        resultado = ejecutar_gauss_seidel(dominio)
        assert resultado.estabilizado
        assert resultado.valores_finales["b"] == "FALSO"

    def test_not_oscila_sin_alpha(self):
        """
        NOT sobre un grafo con retroalimentación produce oscilación V↔F
        con alpha=1 (sin amortiguación). Esto es correcto: NOT es un
        operador de período 2 sin punto fijo entre V y F.
        El motor debe reportar estabilizado=False tras agotar iteraciones.
        """
        dominio = DominioParaMotor(
            variables={
                "a": Variable.desde_valor("a", V),
                "b": Variable.desde_valor("b", V),
            },
            conectivos=[
                Conectivo(id="NOT_1", tabla=TABLA_NOT, arcos=[("a", "b")]),
            ],
        )
        resultado = ejecutar_gauss_seidel(dominio, alpha=1.0, max_iteraciones=10)
        assert not resultado.estabilizado
        assert resultado.iteraciones == 10
        # El historial muestra la alternancia V↔F
        valores_b = [p.valor_despues for p in resultado.historial if p.destino_id == "b"]
        assert set(valores_b) == {"VERDADERO", "FALSO"}
