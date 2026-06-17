"""
Servicio de propagación — EPiC Playground PoC

Responsabilidad:
  Ejecutar AMBOS algoritmos (Jacobi y Gauss-Seidel) sobre el mismo dominio
  y devolver sus resultados junto con una comparativa estructurada.

  Cada algoritmo recibe una copia independiente del dominio para no
  interferir entre sí.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from motor.algoritmos.jacobi import ejecutar_jacobi
from motor.algoritmos.gauss_seidel import ejecutar_gauss_seidel
from motor.dominio import DominioParaMotor, ResultadoAlgoritmo


@dataclass
class ComparativaAlgoritmos:
    """Resultado combinado de ambos algoritmos con análisis comparativo."""
    jacobi:       ResultadoAlgoritmo
    gauss_seidel: ResultadoAlgoritmo
    comparativa:  Dict[str, Any]


def _clonar_dominio(dominio: DominioParaMotor) -> DominioParaMotor:
    """Copia profunda del dominio para que cada algoritmo trabaje de forma aislada."""
    return copy.deepcopy(dominio)


def _comparar(
    r_jacobi: ResultadoAlgoritmo,
    r_gs:     ResultadoAlgoritmo,
) -> Dict[str, Any]:
    """
    Genera un resumen comparativo entre Jacobi y Gauss-Seidel.
    """
    coinciden_valores = r_jacobi.valores_finales == r_gs.valores_finales

    diff_valores: Dict[str, Dict[str, str]] = {}
    for vid in set(r_jacobi.valores_finales) | set(r_gs.valores_finales):
        vj = r_jacobi.valores_finales.get(vid, "—")
        vg = r_gs.valores_finales.get(vid, "—")
        if vj != vg:
            diff_valores[vid] = {"jacobi": vj, "gauss_seidel": vg}

    if r_jacobi.estabilizado and r_gs.estabilizado:
        convergencia = (
            "jacobi"
            if r_jacobi.iteraciones <= r_gs.iteraciones
            else "gauss_seidel"
        )
    elif r_jacobi.estabilizado:
        convergencia = "jacobi"
    elif r_gs.estabilizado:
        convergencia = "gauss_seidel"
    else:
        convergencia = "ninguno"

    return {
        "ambos_estabilizaron":    r_jacobi.estabilizado and r_gs.estabilizado,
        "coinciden_valores":      coinciden_valores,
        "diferencias_valores":    diff_valores,
        "iteraciones_jacobi":     r_jacobi.iteraciones,
        "iteraciones_gauss_seidel": r_gs.iteraciones,
        "delta_final_jacobi":     r_jacobi.delta_final,
        "delta_final_gauss_seidel": r_gs.delta_final,
        "convergencia_mas_rapida": convergencia,
    }


def propagar(
    dominio:         DominioParaMotor,
    tolerancia:      float = 1e-6,
    max_iteraciones: int   = 100,
    alpha:           float = 1.0,
) -> ComparativaAlgoritmos:
    """
    Ejecuta Jacobi y Gauss-Seidel sobre copias independientes del dominio
    y retorna sus resultados con análisis comparativo.
    """
    dominio_jacobi = _clonar_dominio(dominio)
    dominio_gs     = _clonar_dominio(dominio)

    resultado_jacobi = ejecutar_jacobi(
        dominio_jacobi,
        tolerancia      = tolerancia,
        max_iteraciones = max_iteraciones,
        alpha           = alpha,
    )

    resultado_gs = ejecutar_gauss_seidel(
        dominio_gs,
        tolerancia      = tolerancia,
        max_iteraciones = max_iteraciones,
        alpha           = alpha,
    )

    return ComparativaAlgoritmos(
        jacobi       = resultado_jacobi,
        gauss_seidel = resultado_gs,
        comparativa  = _comparar(resultado_jacobi, resultado_gs),
    )
