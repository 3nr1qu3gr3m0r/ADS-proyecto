from fastapi import APIRouter

from simulador.servicios.simulacion_servicio import SimulacionServicio

router = APIRouter()

servicio = SimulacionServicio()


@router.post("/api/v1/simulaciones")
def iniciar_simulacion():

    return servicio.iniciar_simulacion()


@router.get("/api/v1/simulaciones/1")
def obtener_estado():

    return servicio.obtener_estado()


@router.put("/api/v1/simulaciones/1/avanzar")
def avanzar_paso():

    return servicio.avanzar_paso()


@router.put("/api/v1/simulaciones/1/pausar")
def pausar():

    return servicio.pausar()