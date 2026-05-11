"""
Esquemas Pydantic — API del Motor EPiC Playground

Validan y documentan los contratos HTTP de entrada y salida.
"""

from __future__ import annotations

from typing import Any, Dict, List, Union

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------

class VariableIn(BaseModel):
    id:    str
    valor: str = Field(
        default="NINGUNO",
        description="Uno de: NINGUNO, VERDADERO, FALSO, AMBOS",
    )

    @field_validator("valor")
    @classmethod
    def valor_valido(cls, v: str) -> str:
        opciones = {"NINGUNO", "VERDADERO", "FALSO", "AMBOS"}
        if v.upper() not in opciones:
            raise ValueError(f"valor debe ser uno de {opciones}")
        return v.upper()


class ConectivoIn(BaseModel):
    id:    str
    tabla: Union[str, List[List[int]]] = Field(
        description="Nombre predefinido ('OR','AND','NOT') o matriz 4×4 de ints (0-3)",
    )
    arcos: List[List[str]] = Field(
        description="Lista de pares [origen_id, destino_id]",
    )


class PropagacionRequest(BaseModel):
    variables:       List[VariableIn]
    conectivos:      List[ConectivoIn]
    tolerancia:      float = Field(default=1e-6,  ge=0,    le=1)
    max_iteraciones: int   = Field(default=100,   ge=1,    le=10_000)
    alpha:           float = Field(default=1.0,   gt=0.0,  le=1.0)


# ---------------------------------------------------------------------------
# Salida
# ---------------------------------------------------------------------------

class PasoCalculoOut(BaseModel):
    iteracion:      int
    metodo:         str
    conectivo_id:   str
    destino_id:     str
    valor_antes:    str
    valor_despues:  str
    vector_antes:   List[float]
    vector_despues: List[float]
    delta:          float


class ResultadoAlgoritmoOut(BaseModel):
    metodo:              str
    estabilizado:        bool
    iteraciones:         int
    delta_final:         float
    valores_finales:     Dict[str, str]
    estados_vectoriales: Dict[str, List[float]]
    matrices_procesadas: Dict[str, List[List[float]]]
    historial:           List[PasoCalculoOut]


class ComparativaOut(BaseModel):
    ambos_estabilizaron:       bool
    coinciden_valores:         bool
    diferencias_valores:       Dict[str, Dict[str, str]]
    iteraciones_jacobi:        int
    iteraciones_gauss_seidel:  int
    delta_final_jacobi:        float
    delta_final_gauss_seidel:  float
    convergencia_mas_rapida:   str


class PropagacionResponse(BaseModel):
    jacobi:       ResultadoAlgoritmoOut
    gauss_seidel: ResultadoAlgoritmoOut
    comparativa:  ComparativaOut
