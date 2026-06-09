from fastapi import APIRouter, HTTPException
from motor.api.esquemas import EntradaCalculo
from motor.servicios.propagacion_servicio import calcular_propagacion

router = APIRouter()


@router.post("/api/v1/redes/{id}/calcular")
def post_calcular_red(id: str, payload: EntradaCalculo):
    if payload.id != id:
        raise HTTPException(
            status_code=400,
            detail="El ID proporcionado en la ruta web no coincide con el ID de la red."
        )

    try:
        network_data = payload.model_dump()
        resultado = calcular_propagacion(network_data)
        return resultado

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fallo en la ejecución interna del Motor EPiC: {str(e)}"
        )
