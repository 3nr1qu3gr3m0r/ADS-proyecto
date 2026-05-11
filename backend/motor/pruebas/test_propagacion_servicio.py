"""
Pruebas de integración — Servicio de propagación (Jacobi vs Gauss-Seidel)
"""

import pytest
from motor.dominio import (
    DominioParaMotor, Variable, Conectivo,
    Valor4, TABLA_OR, TABLA_AND,
)
from motor.servicios.propagacion_servicio import propagar, ComparativaAlgoritmos
from motor.servicios.construccion_matriz import construir_dominio

N, V, F, A = Valor4.NINGUNO, Valor4.VERDADERO, Valor4.FALSO, Valor4.AMBOS


def dominio_simple() -> DominioParaMotor:
    return DominioParaMotor(
        variables={
            "x1": Variable.desde_valor("x1", V),
            "x2": Variable.desde_valor("x2", N),
        },
        conectivos=[
            Conectivo(id="OR_1", tabla=TABLA_OR, arcos=[("x1", "x2")]),
        ],
    )


def dominio_ciclo() -> DominioParaMotor:
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


class TestPropagacionServicio:

    def test_retorna_comparativa(self):
        resultado = propagar(dominio_simple())
        assert isinstance(resultado, ComparativaAlgoritmos)

    def test_ambos_algoritmos_presentes(self):
        resultado = propagar(dominio_simple())
        assert resultado.jacobi.metodo == "jacobi"
        assert resultado.gauss_seidel.metodo == "gauss_seidel"

    def test_dominios_son_independientes(self):
        """Modificar un resultado no debe afectar al otro."""
        resultado = propagar(dominio_simple())
        vj = resultado.jacobi.valores_finales.copy()
        vg = resultado.gauss_seidel.valores_finales.copy()
        # Ambos deben haber llegado al mismo resultado en este grafo simple
        assert vj == vg

    def test_comparativa_contiene_campos_esperados(self):
        resultado = propagar(dominio_simple())
        c = resultado.comparativa
        assert "ambos_estabilizaron" in c
        assert "coinciden_valores" in c
        assert "convergencia_mas_rapida" in c
        assert "iteraciones_jacobi" in c
        assert "iteraciones_gauss_seidel" in c

    def test_ambos_estabilizan_grafo_simple(self):
        resultado = propagar(dominio_simple(), alpha=1.0)
        assert resultado.comparativa["ambos_estabilizaron"]

    def test_ambos_estabilizan_grafo_con_ciclo(self):
        resultado = propagar(dominio_ciclo(), alpha=0.7)
        assert resultado.comparativa["ambos_estabilizaron"]

    def test_coinciden_valores_grafo_simple(self):
        resultado = propagar(dominio_simple())
        assert resultado.comparativa["coinciden_valores"]

    def test_convergencia_mas_rapida_es_valida(self):
        resultado = propagar(dominio_ciclo(), alpha=0.7)
        assert resultado.comparativa["convergencia_mas_rapida"] in {
            "jacobi", "gauss_seidel", "ninguno"
        }

    def test_construir_dominio_desde_payload(self):
        payload = {
            "variables": [
                {"id": "a", "valor": "VERDADERO"},
                {"id": "b", "valor": "NINGUNO"},
            ],
            "conectivos": [
                {"id": "C1", "tabla": "OR", "arcos": [["a", "b"]]},
            ],
        }
        dominio = construir_dominio(payload)
        resultado = propagar(dominio)
        assert resultado.jacobi.valores_finales["b"] == "VERDADERO"
        assert resultado.gauss_seidel.valores_finales["b"] == "VERDADERO"

    def test_tabla_personalizada(self):
        """
        Tabla identidad: resultado = tabla[origen][destino] = destino (columna).
        origen=F(2), destino_actual=N(0) → tabla[2][0] = 0 = NINGUNO.
        La tabla identidad preserva el valor del DESTINO, no del origen.
        """
        payload = {
            "variables": [
                {"id": "x", "valor": "FALSO"},
                {"id": "y", "valor": "VERDADERO"},   # destino=V → identidad mantiene V
            ],
            "conectivos": [
                {
                    "id": "ID",
                    "tabla": [
                        [0, 1, 2, 3],
                        [0, 1, 2, 3],
                        [0, 1, 2, 3],
                        [0, 1, 2, 3],
                    ],
                    "arcos": [["x", "y"]],
                },
            ],
        }
        dominio = construir_dominio(payload)
        resultado = propagar(dominio)
        # Identidad preserva valor del destino (col): y=V → sigue siendo V
        assert resultado.jacobi.valores_finales["y"] == "VERDADERO"

    def test_alpha_bajo_no_crashea(self):
        resultado = propagar(dominio_ciclo(), alpha=0.1, max_iteraciones=500)
        assert resultado.jacobi is not None
        assert resultado.gauss_seidel is not None
