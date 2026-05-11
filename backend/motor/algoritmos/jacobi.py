"""
Algoritmo de Jacobi para propagación matricial — EPiC Playground PoC

Característica clave de Jacobi:
  Todos los nuevos valores se calculan usando SOLO los valores del inicio
  de la iteración. Ninguna variable ve los cambios de sus vecinas hasta
  que termina la iteración completa.

  Esto garantiza independencia entre cálculos dentro de una misma iteración,
  lo que lo hace paralelizable, pero puede requerir más iteraciones que
  Gauss-Seidel para converger.
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
    Valor4,
    normalizar,
    a_vector,
)

METODO = "jacobi"


def _propagar_con_snapshot(
    conectivo: Conectivo,
    snapshot: Dict[str, Variable],   # variables congeladas al inicio de la iteración
    variables_actuales: Dict[str, Variable],
    alpha: float,
    iteracion: int,
) -> tuple[Dict[str, np.ndarray], List[PasoCalculo]]:
    """
    Propaga un conectivo usando el snapshot (Jacobi).
    Los valores de ORIGEN vienen del snapshot, nunca de variables_actuales.
    """
    acumulados: Dict[str, List[np.ndarray]] = {}

    for origen_id, destino_id in conectivo.arcos:
        if origen_id not in snapshot:
            raise KeyError(f"Variable origen '{origen_id}' no existe.")
        if destino_id not in variables_actuales:
            raise KeyError(f"Variable destino '{destino_id}' no existe.")

        # Jacobi: origen tomado del snapshot (inicio de iteración)
        v_origen  = snapshot[origen_id].valor
        v_destino = snapshot[destino_id].valor   # destino también del snapshot

        resultado_discreto = conectivo.aplicar_discreto(v_origen, v_destino)
        resultado_vector   = a_vector(resultado_discreto)
        acumulados.setdefault(destino_id, []).append(resultado_vector)

    nuevos: Dict[str, np.ndarray] = {}
    pasos:  List[PasoCalculo]     = []

    for destino_id, vectores in acumulados.items():
        promedio   = normalizar(np.mean(vectores, axis=0))
        actual     = variables_actuales[destino_id].vector
        mezclado   = normalizar((1 - alpha) * actual + alpha * promedio)

        delta      = float(np.max(np.abs(mezclado - actual)))
        valor_ant  = variables_actuales[destino_id].valor

        nuevos[destino_id] = mezclado

        # Aplicar para leer valor nuevo
        tmp = Variable(id=destino_id)
        tmp.actualizar_vector(mezclado)

        pasos.append(PasoCalculo(
            iteracion      = iteracion,
            metodo         = METODO,
            conectivo_id   = conectivo.id,
            destino_id     = destino_id,
            valor_antes    = valor_ant.name,
            valor_despues  = tmp.valor.name,
            vector_antes   = actual.round(8).tolist(),
            vector_despues = mezclado.round(8).tolist(),
            delta          = round(delta, 10),
        ))

    return nuevos, pasos


def ejecutar_jacobi(
    dominio: DominioParaMotor,
    tolerancia:      float = 1e-6,
    max_iteraciones: int   = 100,
    alpha:           float = 1.0,
) -> ResultadoAlgoritmo:
    """
    Ejecuta la propagación matricial con el método de Jacobi.

    En cada iteración:
      1. Se toma un snapshot completo de todas las variables.
      2. Todos los conectivos propagan usando ese snapshot (valores fijos).
      3. Al final de la iteración se aplican todos los cambios.
      4. Se verifica la condición de estabilización.
    """
    historial:    List[PasoCalculo] = []
    delta_final:  float             = float("inf")
    estabilizado: bool              = False
    iteracion:    int               = 0

    for iteracion in range(1, max_iteraciones + 1):
        # --- Snapshot del inicio de iteración (clave de Jacobi) ---
        snapshot = dominio.clonar_variables()

        delta_iteracion = 0.0
        cambios_pendientes: Dict[str, np.ndarray] = {}
        pasos_iteracion:    List[PasoCalculo]      = []

        for conectivo in dominio.conectivos:
            nuevos, pasos = _propagar_con_snapshot(
                conectivo, snapshot, dominio.variables, alpha, iteracion
            )
            # Acumular — si dos conectivos tocan el mismo destino, promediar
            for vid, vec in nuevos.items():
                if vid in cambios_pendientes:
                    cambios_pendientes[vid] = normalizar(
                        cambios_pendientes[vid] + vec
                    )
                else:
                    cambios_pendientes[vid] = vec
            pasos_iteracion.extend(pasos)

        # --- Aplicar todos los cambios al final (Jacobi) ---
        for vid, vec_nuevo in cambios_pendientes.items():
            vec_ant = dominio.variables[vid].vector
            delta   = float(np.max(np.abs(vec_nuevo - vec_ant)))
            delta_iteracion = max(delta_iteracion, delta)
            dominio.variables[vid].actualizar_vector(vec_nuevo)

        historial.extend(pasos_iteracion)
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
