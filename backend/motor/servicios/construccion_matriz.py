"""
Servicio de construcción de matriz — EPiC Playground PoC

Responsabilidad: construir un DominioParaMotor a partir de datos crudos
(dicts/listas), tal como los entregaría el Editor o la API.
"""

from __future__ import annotations

from typing import Any, Dict, List

from motor.dominio import (
    Conectivo,
    DominioParaMotor,
    TablaDeLookup,
    Valor4,
    Variable,
    TABLA_AND,
    TABLA_OR,
    TABLA_NOT,
)

# Tablas predefinidas accesibles por nombre
TABLAS_PREDEFINIDAS: Dict[str, TablaDeLookup] = {
    "OR":  TABLA_OR,
    "AND": TABLA_AND,
    "NOT": TABLA_NOT,
}


def _resolver_tabla(raw: Any) -> TablaDeLookup:
    """
    Acepta:
      - str: nombre de tabla predefinida ("OR", "AND", "NOT")
      - list[list[int]]: tabla numérica 4×4 con ordinales de Valor4
    """
    if isinstance(raw, str):
        nombre = raw.upper()
        if nombre not in TABLAS_PREDEFINIDAS:
            raise ValueError(
                f"Tabla predefinida '{nombre}' no existe. "
                f"Opciones: {list(TABLAS_PREDEFINIDAS)}"
            )
        return TABLAS_PREDEFINIDAS[nombre]

    if isinstance(raw, list):
        tabla: TablaDeLookup = []
        for fila in raw:
            tabla.append([Valor4(int(x)) for x in fila])
        return tabla

    raise TypeError(f"Tipo de tabla no soportado: {type(raw)}")


def construir_dominio(payload: Dict[str, Any]) -> DominioParaMotor:
    """
    Construye un DominioParaMotor desde un payload dict.

    Formato esperado:
    {
        "variables": [
            {"id": "x1", "valor": "VERDADERO"},
            {"id": "x2", "valor": "NINGUNO"},
            ...
        ],
        "conectivos": [
            {
                "id": "C1",
                "tabla": "OR",          # nombre predefinido o lista 4×4 de ints
                "arcos": [["x1", "x2"]]
            },
            ...
        ]
    }
    """
    # --- Variables ---
    variables: Dict[str, Variable] = {}
    for v_raw in payload.get("variables", []):
        vid   = v_raw["id"]
        valor = Valor4[v_raw.get("valor", "NINGUNO").upper()]
        variables[vid] = Variable.desde_valor(vid, valor)

    # --- Conectivos ---
    conectivos: List[Conectivo] = []
    for c_raw in payload.get("conectivos", []):
        tabla = _resolver_tabla(c_raw["tabla"])
        arcos = [tuple(a) for a in c_raw["arcos"]]
        conectivos.append(Conectivo(
            id    = c_raw["id"],
            tabla = tabla,
            arcos = arcos,
        ))

    return DominioParaMotor(variables=variables, conectivos=conectivos)
