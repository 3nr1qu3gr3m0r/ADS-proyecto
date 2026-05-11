"""
Rutas FastAPI — Motor EPiC Playground

Endpoints:
  POST /propagar   — corre Jacobi + Gauss-Seidel y devuelve comparativa
  GET  /salud      — health check
  GET  /tablas     — lista tablas de verdad predefinidas disponibles
"""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from motor.api.esquemas import (
    PropagacionRequest,
    PropagacionResponse,
    ResultadoAlgoritmoOut,
    ComparativaOut,
    PasoCalculoOut,
)
from motor.servicios.construccion_matriz import construir_dominio, TABLAS_PREDEFINIDAS
from motor.servicios.propagacion_servicio import propagar
from motor.dominio import ResultadoAlgoritmo, PasoCalculo

router = APIRouter(prefix="/motor", tags=["Motor de propagaciones"])


# ---------------------------------------------------------------------------
# Helpers de conversión
# ---------------------------------------------------------------------------

def _pasos_out(pasos: list[PasoCalculo]) -> list[PasoCalculoOut]:
    return [PasoCalculoOut(**asdict(p)) for p in pasos]


def _resultado_out(r: ResultadoAlgoritmo) -> ResultadoAlgoritmoOut:
    return ResultadoAlgoritmoOut(
        metodo              = r.metodo,
        estabilizado        = r.estabilizado,
        iteraciones         = r.iteraciones,
        delta_final         = r.delta_final,
        valores_finales     = r.valores_finales,
        estados_vectoriales = r.estados_vectoriales,
        matrices_procesadas = r.matrices_procesadas,
        historial           = _pasos_out(r.historial),
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/salud", summary="Health check del Motor")
def salud() -> dict:
    return {"estado": "ok", "componente": "motor"}


@router.get("/tablas", summary="Tablas de verdad predefinidas disponibles")
def tablas_disponibles() -> dict:
    return {
        "tablas": list(TABLAS_PREDEFINIDAS.keys()),
        "descripcion": {
            "OR":  "Disyunción de Belnap sobre dominio de 4 valores",
            "AND": "Conjunción de Belnap sobre dominio de 4 valores",
            "NOT": "Negación de Belnap sobre dominio de 4 valores",
        },
    }


@router.post(
    "/propagar",
    response_model=PropagacionResponse,
    summary="Propagar valores mediante Jacobi y Gauss-Seidel",
    description=(
        "Recibe variables, conectivos y arcos. "
        "Ejecuta ambos algoritmos de forma independiente y devuelve "
        "los resultados junto con un análisis comparativo."
    ),
)
def propagar_endpoint(body: PropagacionRequest) -> PropagacionResponse:
    # Construir payload para el servicio
    payload = {
        "variables": [v.model_dump() for v in body.variables],
        "conectivos": [
            {
                "id":    c.id,
                "tabla": c.tabla,
                "arcos": c.arcos,
            }
            for c in body.conectivos
        ],
    }

    try:
        dominio = construir_dominio(payload)
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(status_code=422, detail=str(e))

    try:
        comparativa = propagar(
            dominio,
            tolerancia      = body.tolerancia,
            max_iteraciones = body.max_iteraciones,
            alpha           = body.alpha,
        )
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=500, detail=str(e))

    return PropagacionResponse(
        jacobi       = _resultado_out(comparativa.jacobi),
        gauss_seidel = _resultado_out(comparativa.gauss_seidel),
        comparativa  = ComparativaOut(**comparativa.comparativa),
    )
