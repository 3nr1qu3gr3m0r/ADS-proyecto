"""
validadores.py — Validación pura del grafo (port desde frontend tipos.ts)
"""

from .modelos import Nodo, Arista, Red, ErrorValidacion


TIPOS_NODO = {"AND", "OR", "NOT"}


def validar_nodo(nodo: Nodo, ids_existentes: set[str] | None = None) -> list[ErrorValidacion]:
    errores: list[ErrorValidacion] = []

    if not nodo.id:
        errores.append(ErrorValidacion(codigo="NODO_SIN_ID", mensaje="El nodo no tiene identificador."))
    elif not nodo.id.startswith("nodo-"):
        errores.append(ErrorValidacion(
            codigo="NODO_FORMATO_INVALIDO",
            mensaje=f'El identificador "{nodo.id}" debe seguir el formato "nodo-*".',
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
            codigo="NODO_SIN_NOMBRE",
            mensaje=f'El nodo "{nodo.id}" no tiene etiqueta.',
            nodo_id=nodo.id,
        ))

    if nodo.tipo not in TIPOS_NODO:
        errores.append(ErrorValidacion(
            codigo="TIPO_NODO_INVALIDO",
            mensaje=f'El tipo "{nodo.tipo}" debe ser uno de: {", ".join(TIPOS_NODO)}.',
            nodo_id=nodo.id,
        ))

    if not isinstance(nodo.propiedades, dict):
        errores.append(ErrorValidacion(
            codigo="PROPIEDADES_INVALIDAS",
            mensaje=f'El nodo "{nodo.id}" tiene propiedades que no son un objeto.',
            nodo_id=nodo.id,
        ))

    if not _es_finito(nodo.posicion.x) or not _es_finito(nodo.posicion.y):
        errores.append(ErrorValidacion(
            codigo="POSICION_INVALIDA",
            mensaje=f'El nodo "{nodo.id}" tiene coordenadas inválidas.',
            nodo_id=nodo.id,
        ))

    return errores


def validar_arista(
    arista: Arista,
    ids_nodos: set[str],
    ids_aristas: set[str] | None = None,
) -> list[ErrorValidacion]:
    errores: list[ErrorValidacion] = []

    if not arista.id:
        errores.append(ErrorValidacion(codigo="ARISTA_SIN_ID", mensaje="La arista no tiene identificador."))
    elif not arista.id.startswith("arista-"):
        errores.append(ErrorValidacion(
            codigo="ARISTA_FORMATO_INVALIDO",
            mensaje=f'El identificador "{arista.id}" debe seguir el formato "arista-*".',
            arista_id=arista.id,
        ))

    if ids_aristas and arista.id in ids_aristas:
        errores.append(ErrorValidacion(
            codigo="ARISTA_DUPLICADA",
            mensaje=f'Ya existe una arista con id "{arista.id}".',
            arista_id=arista.id,
        ))

    if not ids_nodos or arista.id_origen not in ids_nodos:
        errores.append(ErrorValidacion(
            codigo="ORIGEN_INEXISTENTE",
            mensaje=f'La arista "{arista.id}" referencia un nodo origen inexistente.',
            arista_id=arista.id,
        ))

    if not ids_nodos or arista.id_destino not in ids_nodos:
        errores.append(ErrorValidacion(
            codigo="DESTINO_INEXISTENTE",
            mensaje=f'La arista "{arista.id}" referencia un nodo destino inexistente.',
            arista_id=arista.id,
        ))

    if arista.id_origen == arista.id_destino:
        errores.append(ErrorValidacion(
            codigo="AUTO_LOOP",
            mensaje=f'La arista "{arista.id}" no puede conectar un nodo consigo mismo.',
            arista_id=arista.id,
        ))

    if not _es_finito(arista.peso):
        errores.append(ErrorValidacion(
            codigo="PESO_INVALIDO",
            mensaje=f'La arista "{arista.id}" tiene un peso inválido: {arista.peso}.',
            arista_id=arista.id,
        ))

    return errores


def validar_matriz(matriz) -> list[ErrorValidacion]:
    errores: list[ErrorValidacion] = []

    if not hasattr(matriz, "id") or not matriz.id:
        errores.append(ErrorValidacion(codigo="MATRIZ_SIN_ID", mensaje="La matriz no tiene identificador."))

    if not hasattr(matriz, "valores") or not matriz.valores:
        errores.append(ErrorValidacion(codigo="MATRIZ_VACIA", mensaje=f"La matriz no tiene valores."))
        return errores

    filas = matriz.valores
    cols = len(filas[0]) if filas else 0

    if cols == 0:
        errores.append(ErrorValidacion(
            codigo="MATRIZ_VACIA",
            mensaje=f"La matriz tiene 0 columnas.",
        ))
        return errores

    for i, fila in enumerate(filas):
        if len(fila) != cols:
            errores.append(ErrorValidacion(
                codigo="MATRIZ_FILA_HETEROGENEA",
                mensaje=f"La fila {i} tiene {len(fila)} columnas, se esperaban {cols}.",
            ))

    for i, fila in enumerate(filas):
        for j, valor in enumerate(fila):
            if not isinstance(valor, (int, float)) or not _es_finito(valor):
                errores.append(ErrorValidacion(
                    codigo="MATRIZ_VALOR_INVALIDO",
                    mensaje=f"El valor en [{i}][{j}] no es numérico o es infinito.",
                ))

    return errores


def validar_red(red: Red) -> list[ErrorValidacion]:
    errores: list[ErrorValidacion] = []

    if not red.id:
        errores.append(ErrorValidacion(codigo="RED_SIN_ID", mensaje="La red no tiene identificador."))

    if not red.nodos or len(red.nodos) == 0:
        errores.append(ErrorValidacion(codigo="GRAFO_VACIO", mensaje="La red no contiene nodos."))
        return errores

    ids_nodos: set[str] = set()
    ids_aristas: set[str] = set()

    for nodo in red.nodos:
        errores_nodo = validar_nodo(nodo, ids_nodos)
        errores.extend(errores_nodo)
        if nodo.id and nodo.id not in ids_nodos:
            ids_nodos.add(nodo.id)

    for arista in red.aristas:
        errores_arista = validar_arista(arista, ids_nodos, ids_aristas)
        errores.extend(errores_arista)
        if arista.id and arista.id not in ids_aristas:
            ids_aristas.add(arista.id)

    if red.aristas and _detectar_ciclos(red.nodos, red.aristas):
        errores.append(ErrorValidacion(
            codigo="CICLO_DETECTADO",
            mensaje="La red contiene uno o más ciclos dirigidos.",
        ))

    return errores


def _detectar_ciclos(nodos: list[Nodo], aristas: list[Arista]) -> bool:
    ady: dict[str, list[str]] = {n.id: [] for n in nodos}
    for a in aristas:
        if a.id_origen in ady:
            ady[a.id_origen].append(a.id_destino)

    color: dict[str, int] = {n.id: 0 for n in nodos}  # 0=blanco,1=gris,2=negro

    def dfs(nid: str) -> bool:
        color[nid] = 1
        for v in ady.get(nid, []):
            c = color.get(v, 0)
            if c == 1:
                return True
            if c == 0 and dfs(v):
                return True
        color[nid] = 2
        return False

    for n in nodos:
        if color.get(n.id, 0) == 0 and dfs(n.id):
            return True

    return False


def _es_finito(valor) -> bool:
    return isinstance(valor, (int, float)) and float(valor) != float('inf') and valor == valor