# ============ PROMPT ============
# Implementa el motor de propagación EPiC usando exclusivamente tablas de verdad
# sobre lógica Belnap de 4 valores (T/F/B/N) con ordenamiento topológico (Kahn),
# punto fijo iterativo (máx 100 iteraciones) y consulta por tipo de operador
# (NOT, AND, OR, XOR, IMP) leyendo los valores más recientes en cada pasada.
# ======== FIN DEL PROMPT ========

"""
algoritmos.py — Motor de propagación EPiC por tablas de verdad (Belnap).

Cómo funciona
─────────────
1. Se ordenan los nodos topológicamente: primero las premisas, luego los
   operadores en orden de dependencia (el que depende de otro va después).
2. Se recorre la lista una sola vez. Cada nodo lee los valores que sus
   predecesores ya calcularon en ESTE mismo recorrido y consulta la tabla.
3. Se repite si hay ciclos, hasta que ningún valor cambie (punto fijo).
   Para redes sin ciclos (lo normal) converge en UNA sola pasada.

No hay Jacobi ni Gauss-Seidel: solo tablas de verdad + orden correcto.

Tablas de verdad EPiC (Belnap, 4 valores)
──────────────────────────────────────────
Modelo bitpair: (bit_negativo, bit_positivo)
  N = (0,0)  F = (1,0)  T = (0,1)  B = (1,1)

  NEG(a)    = swap de bits
  AND(a,b)  = (max(neg), min(pos))   — "tan fuerte como la entrada más débil"
  OR(a,b)   = (min(neg), max(pos))   — "tan fuerte como la entrada más fuerte"
  XOR(a,b)  = OR(AND(a,NEG(b)), AND(NEG(a),b))   — exclusivo
  IMP(a,b)  = OR(NEG(a), b)          — implicación material a → b
              requiere EXACTAMENTE 2 entradas: [antecedente, consecuente]
"""

from __future__ import annotations
from collections import deque

from compartido.contratos import IMotorCalculoIterativo, RedInvalidaError
from compartido.modelos import Red, ResultadoPropagacion

# ── Tablas de verdad ──────────────────────────────────────────────────────────

NEG_TABLE: dict[str, str] = {
    "N": "N",
    "T": "F",
    "F": "T",
    "B": "B",
}

AND_TABLE: dict[tuple[str, str], str] = {
    ("N","N"):"N", ("N","F"):"F", ("N","T"):"N", ("N","B"):"F",
    ("F","N"):"F", ("F","F"):"F", ("F","T"):"F", ("F","B"):"F",
    ("T","N"):"N", ("T","F"):"F", ("T","T"):"T", ("T","B"):"B",
    ("B","N"):"F", ("B","F"):"F", ("B","T"):"B", ("B","B"):"B",
}

OR_TABLE: dict[tuple[str, str], str] = {
    ("N","N"):"N", ("N","F"):"N", ("N","T"):"T", ("N","B"):"T",
    ("F","N"):"N", ("F","F"):"F", ("F","T"):"T", ("F","B"):"B",
    ("T","N"):"T", ("T","F"):"T", ("T","T"):"T", ("T","B"):"T",
    ("B","N"):"T", ("B","F"):"B", ("B","T"):"T", ("B","B"):"B",
}

XOR_TABLE: dict[tuple[str, str], str] = {
    # T⊕T=F (exclusivo), B⊕cualquiera=B (contradicción se propaga)
    ("N","N"):"N", ("N","F"):"N", ("N","T"):"N", ("N","B"):"F",
    ("F","N"):"N", ("F","F"):"F", ("F","T"):"T", ("F","B"):"B",
    ("T","N"):"N", ("T","F"):"T", ("T","T"):"F", ("T","B"):"B",
    ("B","N"):"F", ("B","F"):"B", ("B","T"):"B", ("B","B"):"B",
}

IMP_TABLE: dict[tuple[str, str], str] = {
    # IMP(a,b) = OR(NEG(a), b)   →   a → b
    # Requiere exactamente 2 entradas: [antecedente, consecuente]
    # Casos clásicos: T→T=T, T→F=F, F→T=T, F→F=T
    ("T","T"):"T", ("T","F"):"F", ("T","B"):"B", ("T","N"):"N",
    ("F","T"):"T", ("F","F"):"T", ("F","B"):"T", ("F","N"):"T",
    ("B","T"):"T", ("B","F"):"B", ("B","B"):"B", ("B","N"):"T",
    ("N","T"):"T", ("N","F"):"N", ("N","B"):"T", ("N","N"):"N",
}

MAX_ITERACIONES = 100


# ── Función de consulta de tabla ─────────────────────────────────────────────

def aplicar_operador(tipo: str, entradas: list[str]) -> str:
    """Aplica el operador consultando SOLO la tabla correspondiente."""
    if not entradas:
        return "N"

    if tipo == "NOT":
        return NEG_TABLE[entradas[0]]

    if tipo == "IMP":
        # Requiere exactamente 2: [antecedente, consecuente]
        return IMP_TABLE[(entradas[0], entradas[1])]

    if tipo == "AND":
        resultado = entradas[0]
        for v in entradas[1:]:
            resultado = AND_TABLE[(resultado, v)]
        return resultado

    if tipo == "OR":
        resultado = entradas[0]
        for v in entradas[1:]:
            resultado = OR_TABLE[(resultado, v)]
        return resultado

    if tipo == "XOR":
        resultado = entradas[0]
        for v in entradas[1:]:
            resultado = XOR_TABLE[(resultado, v)]
        return resultado

    return "N"


# ── Ordenamiento topológico ───────────────────────────────────────────────────

def _orden_topologico(red: Red) -> list[str]:
    """
    Devuelve los IDs de nodos en orden de dependencia usando Kahn.
    Los nodos con 0 entradas (premisas y huérfanos) van primero.
    Si hay ciclos, los nodos del ciclo se agregan al final tal como están.
    """
    grado: dict[str, int] = {n.id: 0 for n in red.nodos}
    hijos: dict[str, list[str]] = {n.id: [] for n in red.nodos}

    for a in red.aristas:
        if a.id_destino in grado:
            grado[a.id_destino] += 1
        if a.id_origen in hijos:
            hijos[a.id_origen].append(a.id_destino)

    cola  = deque(nid for nid, g in grado.items() if g == 0)
    orden: list[str] = []

    while cola:
        nid = cola.popleft()
        orden.append(nid)
        for hijo in hijos[nid]:
            grado[hijo] -= 1
            if grado[hijo] == 0:
                cola.append(hijo)

    # Nodos en ciclos: agregar al final
    procesados = set(orden)
    for n in red.nodos:
        if n.id not in procesados:
            orden.append(n.id)

    return orden


# ── Motor ─────────────────────────────────────────────────────────────────────

class MotorTablas(IMotorCalculoIterativo):
    """
    Propaga valores usando EXCLUSIVAMENTE las tablas de verdad EPiC.
    Procesa los nodos en orden topológico para que cada nodo lea el
    valor ya calculado de sus predecesores en el mismo recorrido.
    Para redes sin ciclos converge en UNA sola pasada.
    """

    def calcular(self, red: Red) -> ResultadoPropagacion:
        return self.calcular_pasos(red)[-1]

    def calcular_pasos(self, red: Red) -> list[ResultadoPropagacion]:
        try:
            _verificar_red(red)
        except RedInvalidaError as exc:
            return [ResultadoPropagacion(
                red_id=red.id, iteraciones=0, valores_nodos={},
                convergido=False, error=str(exc),
            )]

        # Entradas de cada nodo: lista de IDs origen en orden de conexión
        entradas: dict[str, list[str]] = {n.id: [] for n in red.nodos}
        for a in red.aristas:
            if a.id_destino in entradas:
                entradas[a.id_destino].append(a.id_origen)

        # Orden de procesamiento: topológico
        orden = _orden_topologico(red)

        # Estado inicial: premisas con su valor, operadores en N
        valores: dict[str, str] = {}
        for n in red.nodos:
            valores[n.id] = n.valor_premisa if n.es_premisa else "N"

        pasos: list[ResultadoPropagacion] = []

        # Paso 0: estado inicial (antes de consultar ninguna tabla)
        pasos.append(ResultadoPropagacion(
            red_id=red.id, iteraciones=0,
            valores_nodos=dict(valores), convergido=False, error=None,
        ))

        for iteracion in range(1, MAX_ITERACIONES + 1):
            nuevos = dict(valores)
            cambiado = False

            for nid in orden:
                nodo = next(n for n in red.nodos if n.id == nid)
                if nodo.es_premisa:
                    continue

                # Lee los valores MÁS RECIENTES (ya actualizados en esta misma pasada)
                vals_entrada = [nuevos[src] for src in entradas[nid]]
                nuevo_valor  = aplicar_operador(nodo.tipo, vals_entrada)

                if nuevo_valor != valores[nid]:
                    cambiado = True
                nuevos[nid] = nuevo_valor

            valores = nuevos
            convergido = not cambiado

            pasos.append(ResultadoPropagacion(
                red_id=red.id, iteraciones=iteracion,
                valores_nodos=dict(valores),
                convergido=convergido, error=None,
            ))

            if convergido:
                break

        return pasos


def _verificar_red(red: Red) -> None:
    ids = {n.id for n in red.nodos}
    for a in red.aristas:
        if a.id_origen not in ids:
            raise RedInvalidaError(f'Nodo origen "{a.id_origen}" no existe.')
        if a.id_destino not in ids:
            raise RedInvalidaError(f'Nodo destino "{a.id_destino}" no existe.')


def obtener_motor() -> MotorTablas:
    return MotorTablas()
