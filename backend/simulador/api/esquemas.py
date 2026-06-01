from pydantic import BaseModel
from typing import List


class ResultadoPropagacionSchema(BaseModel):

    red_id: str

    iteraciones: int

    valores_nodos: dict

    convergido: bool

    error: str | None = None


class SalidaSimulacion(BaseModel):

    fase: str

    paso_actual: int

    historial: List[ResultadoPropagacionSchema]