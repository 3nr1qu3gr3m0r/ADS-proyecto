from pydantic import BaseModel
from typing import List, Optional

class PropiedadesNodo(BaseModel):
    valor: Optional[str] = "N"
    premisa: Optional[bool] = False
    entradas: Optional[int] = None

class NodoInput(BaseModel):
    id: str
    tipo: str
    etiqueta: str
    propiedades: Optional[PropiedadesNodo] = None

class AristaInput(BaseModel):
    id: str
    idOrigen: str
    idDestino: str
    peso: Optional[int] = 1

class EntradaCalculo(BaseModel):
    id: str
    nodos: List[NodoInput]
    aristas: List[AristaInput]
    version: Optional[int] = 1
