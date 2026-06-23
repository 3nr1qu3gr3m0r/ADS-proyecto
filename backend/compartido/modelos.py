"""
modelos.py — Entidades del dominio compartido.

Tipos de nodo:
  - "premisa" : valor fijo T/F/B/N asignado por el usuario; solo salidas, nunca entradas.
  - "AND"/"OR"/"XOR"/"NOT" : valor calculado por las tablas de verdad EPiC.

Valores evidenciales (Belnap 4-valores):
  T = Verdadero     (solo evidencia positiva)
  F = Falso         (solo evidencia negativa)
  B = Ambos         (contradicción: evidencia positiva Y negativa)
  N = Ninguno       (sin evidencia)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

VALOR_INICIAL_PREMISA = "T"
VALOR_INICIAL_OPERADOR = "N"


@dataclass
class Posicion:
    x: float = 0.0
    y: float = 0.0

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y}

    @classmethod
    def from_dict(cls, data: dict) -> "Posicion":
        return cls(x=float(data.get("x", 0)), y=float(data.get("y", 0)))


@dataclass
class Nodo:
    id: str
    etiqueta: str
    tipo: str   # "premisa" | "AND" | "OR" | "XOR" | "NOT"
    propiedades: dict = field(default_factory=dict)
    #   premisa  → {"valor": "T"|"F"|"B"|"N"}
    #   operador → {}   (valor lo calcula el Motor)
    posicion: Posicion = field(default_factory=Posicion)

    @property
    def es_premisa(self) -> bool:
        return self.tipo == "premisa"

    @property
    def valor_premisa(self) -> str:
        """Valor evidencial fijo de este nodo si es premisa."""
        return str(self.propiedades.get("valor", VALOR_INICIAL_PREMISA))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "etiqueta": self.etiqueta,
            "tipo": self.tipo,
            "propiedades": dict(self.propiedades),
            "posicion": self.posicion.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Nodo":
        return cls(
            id=data["id"],
            etiqueta=data["etiqueta"],
            tipo=data["tipo"],
            propiedades=dict(data.get("propiedades", {})),
            posicion=Posicion.from_dict(data.get("posicion", {})),
        )


@dataclass
class Arista:
    id: str
    id_origen: str   # JSON: "idOrigen"
    id_destino: str  # JSON: "idDestino"
    peso: float = 1.0
    metadatos: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "idOrigen": self.id_origen,
            "idDestino": self.id_destino,
            "peso": self.peso,
            "metadatos": dict(self.metadatos),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Arista":
        return cls(
            id=data["id"],
            id_origen=data["idOrigen"],
            id_destino=data["idDestino"],
            peso=float(data.get("peso", 1.0)),
            metadatos=dict(data.get("metadatos", {})),
        )


@dataclass
class Red:
    id: str
    nodos: list[Nodo] = field(default_factory=list)
    aristas: list[Arista] = field(default_factory=list)
    version: int = 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nodos": [n.to_dict() for n in self.nodos],
            "aristas": [a.to_dict() for a in self.aristas],
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Red":
        return cls(
            id=data["id"],
            nodos=[Nodo.from_dict(n) for n in data.get("nodos", [])],
            aristas=[Arista.from_dict(a) for a in data.get("aristas", [])],
            version=int(data.get("version", 0)),
        )


@dataclass
class ResultadoPropagacion:
    red_id: str
    iteraciones: int = 0
    valores_nodos: dict = field(default_factory=dict)   # {"nodo-001": "T"|"F"|"B"|"N"}
    convergido: bool = False
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "redId": self.red_id,
            "iteraciones": self.iteraciones,
            "valoresNodos": dict(self.valores_nodos),
            "convergido": self.convergido,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ResultadoPropagacion":
        return cls(
            red_id=data["redId"],
            iteraciones=int(data.get("iteraciones", 0)),
            valores_nodos=dict(data.get("valoresNodos", {})),
            convergido=bool(data.get("convergido", False)),
            error=data.get("error"),
        )


@dataclass
class EstadoSimulacion:
    fase: str
    paso_actual: int = 0
    historial: list[ResultadoPropagacion] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "fase": self.fase,
            "pasoActual": self.paso_actual,
            "historial": [h.to_dict() for h in self.historial],
        }


@dataclass
class ErrorValidacion:
    codigo: str
    mensaje: str
    nodo_id: Optional[str] = None
    arista_id: Optional[str] = None

    def to_dict(self) -> dict:
        d: dict = {"codigo": self.codigo, "mensaje": self.mensaje}
        if self.nodo_id is not None:
            d["nodoId"] = self.nodo_id
        if self.arista_id is not None:
            d["aristaId"] = self.arista_id
        return d
