"""
Algoritmo de Gauss-Seidel para propagación matricial — EPiC Playground PoC

Característica clave de Gauss-Seidel:
  Cada variable usa los valores MÁS RECIENTES disponibles en el momento
  de su cálculo. A diferencia de Jacobi, no hay snapshot: si una variable
  ya fue actualizada en esta iteración, sus vecinas verán el nuevo valor
  inmediatamente.

  Esto generalmente acelera la convergencia respecto a Jacobi, pero los
  cálculos son secuenciales y el orden de los conectivos importa.
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np

from motor.dominio import (
    Conectivo,
    DominioParaMotor,
    PasoCalculo,
    ResultadoAlgoritmo,
    Variable,
    normalizar,
    a_vector,
)

METODO = "gauss_seidel"


def _propagar_conectivo(
    conectivo: Conectivo,
    variables: Dict[str, Variable],   # estado vivo — se lee y escribe en el momento
    alpha: float,
    iteracion: int,
) -> tuple[float, List[PasoCalculo]]:
    """
    Propaga un conectivo con Gauss-Seidel.
    Cada arco lee el valor MÁS RECIENTE de su origen (puede haber cambiado
    en esta misma iteración).
    Retorna el delta máximo producido y los pasos registrados.
    """
    acumulados: Dict[str, List[np.ndarray]] = {}

    for origen_id, destino_id in conectivo.arcos:
        if origen_id not in variables:
            raise KeyError(f"Variable origen '{origen_id}' no existe.")
        if destino_id not in variables:
            raise KeyError(f"Variable destino '{destino_id}' no existe.")

        # Gauss-Seidel: se leen valores ACTUALES (ya modificados si aplica)
        v_origen  = variables[origen_id].valor
        v_destino = variables[destino_id].valor

        resultado_discreto = conectivo.aplicar_discreto(v_origen, v_destino)
        resultado_vector   = a_vector(resultado_discreto)
        acumulados.setdefault(destino_id, []).append(resultado_vector)

    delta_max: float          = 0.0
    pasos:     List[PasoCalculo] = []

    for destino_id, vectores in acumulados.items():
        promedio  = normalizar(np.mean(vectores, axis=0))
        actual    = variables[destino_id].vector
        valor_ant = variables[destino_id].valor
        mezclado  = normalizar((1 - alpha) * actual + alpha * promedio)

        delta     = float(np.max(np.abs(mezclado - actual)))
        delta_max = max(delta_max, delta)

        # Gauss-Seidel: actualización inmediata
        variables[destino_id].actualizar_vector(mezclado)

        pasos.append(PasoCalculo(
            iteracion      = iteracion,
            metodo         = METODO,
            conectivo_id   = conectivo.id,
            destino_id     = destino_id,
            valor_antes    = valor_ant.name,
            valor_despues  = variables[destino_id].valor.name,
            vector_antes   = actual.round(8).tolist(),
            vector_despues = variables[destino_id].snapshot(),
            delta          = round(delta, 10),
        ))

    return delta_max, pasos


def ejecutar_gauss_seidel(
    dominio: DominioParaMotor,
    tolerancia:      float = 1e-6,
    max_iteraciones: int   = 100,
    alpha:           float = 1.0,
) -> ResultadoAlgoritmo:
    """
    Ejecuta la propagación matricial con el método de Gauss-Seidel.

    En cada iteración:
      1. Se recorren los conectivos en orden.
      2. Cada conectivo propaga usando los valores más recientes.
      3. Las actualizaciones son inmediatas — el siguiente conectivo las ve.
      4. Se verifica la condición de estabilización.
    """
    historial:    List[PasoCalculo] = []
    delta_final:  float             = float("inf")
    estabilizado: bool              = False
    iteracion:    int               = 0

    for iteracion in range(1, max_iteraciones + 1):
        delta_iteracion = 0.0

        for conectivo in dominio.conectivos:
            delta_conex, pasos = _propagar_conectivo(
                conectivo, dominio.variables, alpha, iteracion
            )
            delta_iteracion = max(delta_iteracion, delta_conex)
            historial.extend(pasos)

        delta_final = delta_iteracion

        if delta_final <= tolerancia:
            estabilizado = True
            break

    return ResultadoAlgoritmo(
        metodo              = METODO,
        estabilizado        = estabilizado,
        iteraciones         = iteracion,
        delta_final         = round(delta_final, 10),
        valores_finales     = dominio.snapshot_discreto(),
        estados_vectoriales = dominio.snapshot_vectorial(),
        matrices_procesadas = {c.id: c.matriz_flotante() for c in dominio.conectivos},
        historial           = historial,
    )
