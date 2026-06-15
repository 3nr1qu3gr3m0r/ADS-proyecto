"""
modelos.py — Modelos de datos del sistema (dataclasses espejo del contrato JSON del README)
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Posicion:
    x: float = 0.0
    y: float = 0.0

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y}

    @classmethod
    def from_dict(cls, data: dict) -> 'Posicion':
        return cls(x=float(data["x"]), y=float(data["y"]))


@dataclass
class Nodo:
    id: str
    tipo: str  # "AND" | "OR" | "NOT"
    etiqueta: str
    propiedades: dict = field(default_factory=dict)
    posicion: Posicion = field(default_factory=Posicion)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tipo": self.tipo,
            "etiqueta": self.etiqueta,
            "propiedades": dict(self.propiedades),
            "posicion": self.posicion.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Nodo':
        return cls(
            id=data["id"],
            tipo=data["tipo"],
            etiqueta=data["etiqueta"],
            propiedades=dict(data.get("propiedades", {})),
            posicion=Posicion.from_dict(data["posicion"]),
        )


@dataclass
class Arista:
    id: str
    id_origen: str  # → JSON: "idOrigen"
    id_destino: str  # → JSON: "idDestino"
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
    def from_dict(cls, data: dict) -> 'Arista':
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
    def from_dict(cls, data: dict) -> 'Red':
        return cls(
            id=data["id"],
            nodos=[Nodo.from_dict(n) for n in data.get("nodos", [])],
            aristas=[Arista.from_dict(a) for a in data.get("aristas", [])],
            version=int(data.get("version", 0)),
        )


@dataclass
class ResultadoPropagacion:
    red_id: str  # → JSON: "redId"
    iteraciones: int = 0
    valores_nodos: dict = field(default_factory=dict)  # → JSON: "valoresNodos" {"nodo-001": 1.0}
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
    def from_dict(cls, data: dict) -> 'ResultadoPropagacion':
        return cls(
            red_id=data["redId"],
            iteraciones=int(data.get("iteraciones", 0)),
            valores_nodos=dict(data.get("valoresNodos", {})),
            convergido=bool(data.get("convergido", False)),
            error=data.get("error"),
        )


@dataclass
class EstadoSimulacion:
    fase: str  # "inactivo" | "corriendo" | "pausado" | "completado" | "error"
    paso_actual: int = 0  # → JSON: "pasoActual"
    historial: list[ResultadoPropagacion] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "fase": self.fase,
            "pasoActual": self.paso_actual,
            "historial": [h.to_dict() for h in self.historial],
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'EstadoSimulacion':
        return cls(
            fase=data["fase"],
            paso_actual=int(data.get("pasoActual", 0)),
            historial=[ResultadoPropagacion.from_dict(h) for h in data.get("historial", [])],
        )


@dataclass
class ErrorValidacion:
    codigo: str
    mensaje: str
    nodo_id: Optional[str] = None  # → JSON: "nodoId"
    arista_id: Optional[str] = None  # → JSON: "aristaId"

    def to_dict(self) -> dict:
        d = {"codigo": self.codigo, "mensaje": self.mensaje}
        if self.nodo_id is not None:
            d["nodoId"] = self.nodo_id
        if self.arista_id is not None:
            d["aristaId"] = self.arista_id
        return d