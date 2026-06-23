# ============ PROMPT ============
# Implementa validación estructural de redes EPiC: verifica que las premisas
# no reciban entradas, que NOT tenga exactamente 1 entrada, que IMP tenga 2,
# que todos los IDs sigan los formatos nodo-*/arista-* y que los valores
# de premisa pertenezcan al conjunto Belnap {T, F, B, N}.
# ======== FIN DEL PROMPT ========

"""
validadores.py — Validación estructural de la red.

Reglas clave del dominio EPiC:
  1. Las PREMISAS solo pueden tener aristas salientes, nunca entrantes.
     Son hechos conocidos (axiomas), no se calculan de otros nodos.
  2. Los nodos NOT deben tener exactamente 1 entrada.
  3. Los ciclos SÍ están permitidos: el algoritmo de punto fijo sobre las
     tablas de verdad los maneja correctamente (el lattice de Belnap
     garantiza terminación porque los valores solo pueden crecer: N→T/F→B).
"""

from __future__ import annotations

from compartido.modelos import Nodo, Arista, Red, ErrorValidacion
from compartido.contratos import TIPOS_OPERADOR, VALORES_BELNAP

TIPOS_VALIDOS = {"premisa"} | TIPOS_OPERADOR


def validar_nodo(nodo: Nodo, ids_existentes: set[str] | None = None) -> list[ErrorValidacion]:
    errores: list[ErrorValidacion] = []

    if not nodo.id or not nodo.id.startswith("nodo-"):
        errores.append(ErrorValidacion(
            codigo="NODO_FORMATO_INVALIDO",
            mensaje=f'El id "{nodo.id}" debe seguir el formato "nodo-*".',
            nodo_id=nodo.id,
        ))

    if ids_existentes and nodo.id in ids_existentes:
        errores.append(ErrorValidacion(
            codigo="NODO_DUPLICADO",
            mensaje=f'Ya existe un nodo con id "{nodo.id}".',
            nodo_id=nodo.id,
        ))

    if not nodo.etiqueta or not nodo.etiqueta.strip():
        errores.append(ErrorValidacion(
            codigo="NODO_SIN_ETIQUETA",
            mensaje=f'El nodo "{nodo.id}" no tiene etiqueta.',
            nodo_id=nodo.id,
        ))

    if nodo.tipo not in TIPOS_VALIDOS:
        errores.append(ErrorValidacion(
            codigo="TIPO_INVALIDO",
            mensaje=f'El tipo "{nodo.tipo}" no es válido. Usa: {sorted(TIPOS_VALIDOS)}.',
            nodo_id=nodo.id,
        ))

    if nodo.tipo == "premisa":
        valor = nodo.propiedades.get("valor", "T")
        if valor not in VALORES_BELNAP:
            errores.append(ErrorValidacion(
                codigo="VALOR_BELNAP_INVALIDO",
                mensaje=f'El valor "{valor}" de la premisa "{nodo.id}" debe ser T, F, B o N.',
                nodo_id=nodo.id,
            ))

    return errores


def validar_arista(
    arista: Arista,
    ids_nodos: set[str],
    tipo_por_id: dict[str, str],
    ids_aristas: set[str] | None = None,
) -> list[ErrorValidacion]:
    errores: list[ErrorValidacion] = []

    if not arista.id or not arista.id.startswith("arista-"):
        errores.append(ErrorValidacion(
            codigo="ARISTA_FORMATO_INVALIDO",
            mensaje=f'El id "{arista.id}" debe seguir el formato "arista-*".',
            arista_id=arista.id,
        ))

    if ids_aristas and arista.id in ids_aristas:
        errores.append(ErrorValidacion(
            codigo="ARISTA_DUPLICADA",
            mensaje=f'Ya existe una arista con id "{arista.id}".',
            arista_id=arista.id,
        ))

    if arista.id_origen not in ids_nodos:
        errores.append(ErrorValidacion(
            codigo="ORIGEN_INEXISTENTE",
            mensaje=f'El nodo origen "{arista.id_origen}" no existe.',
            arista_id=arista.id,
        ))

    if arista.id_destino not in ids_nodos:
        errores.append(ErrorValidacion(
            codigo="DESTINO_INEXISTENTE",
            mensaje=f'El nodo destino "{arista.id_destino}" no existe.',
            arista_id=arista.id,
        ))

    # ⚠️ REGLA CLAVE: las premisas no pueden recibir entradas
    if arista.id_destino in tipo_por_id and tipo_por_id[arista.id_destino] == "premisa":
        errores.append(ErrorValidacion(
            codigo="ENTRADA_A_PREMISA",
            mensaje=(
                f'La arista "{arista.id}" apunta a la premisa "{arista.id_destino}". '
                "Las premisas son hechos fijos y no pueden recibir entradas."
            ),
            arista_id=arista.id,
        ))

    if arista.id_origen == arista.id_destino:
        errores.append(ErrorValidacion(
            codigo="AUTO_LOOP",
            mensaje=f'La arista "{arista.id}" no puede conectar un nodo consigo mismo.',
            arista_id=arista.id,
        ))

    return errores


def validar_red(red: Red) -> list[ErrorValidacion]:
    errores: list[ErrorValidacion] = []

    if not red.id:
        errores.append(ErrorValidacion(codigo="RED_SIN_ID", mensaje="La red no tiene id."))

    if not red.nodos:
        errores.append(ErrorValidacion(codigo="GRAFO_VACIO", mensaje="La red no tiene nodos."))
        return errores

    ids_nodos: set[str] = set()
    ids_aristas: set[str] = set()
    tipo_por_id: dict[str, str] = {}

    for nodo in red.nodos:
        errores.extend(validar_nodo(nodo, ids_nodos))
        if nodo.id:
            ids_nodos.add(nodo.id)
            tipo_por_id[nodo.id] = nodo.tipo

    for arista in red.aristas:
        errores.extend(validar_arista(arista, ids_nodos, tipo_por_id, ids_aristas))
        if arista.id:
            ids_aristas.add(arista.id)

    # Validar que nodos NOT tengan exactamente 1 entrada
    entradas_por_nodo: dict[str, int] = {n.id: 0 for n in red.nodos}
    for a in red.aristas:
        if a.id_destino in entradas_por_nodo:
            entradas_por_nodo[a.id_destino] += 1

    for nodo in red.nodos:
        if nodo.tipo == "NOT" and entradas_por_nodo[nodo.id] != 1:
            errores.append(ErrorValidacion(
                codigo="NOT_ENTRADAS_INVALIDAS",
                mensaje=(
                    f'El nodo NOT "{nodo.id}" necesita exactamente 1 entrada; '
                    f'tiene {entradas_por_nodo[nodo.id]}.'
                ),
                nodo_id=nodo.id,
            ))
        if nodo.tipo == "IMP" and entradas_por_nodo[nodo.id] != 2:
            errores.append(ErrorValidacion(
                codigo="IMP_ENTRADAS_INVALIDAS",
                mensaje=(
                    f'El nodo IMP "{nodo.id}" necesita exactamente 2 entradas '
                    f'(antecedente y consecuente); tiene {entradas_por_nodo[nodo.id]}. '
                    'Conecta primero el antecedente y luego el consecuente.'
                ),
                nodo_id=nodo.id,
            ))

    return errores
