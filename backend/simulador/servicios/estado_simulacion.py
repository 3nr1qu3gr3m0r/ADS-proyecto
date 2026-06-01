from dataclasses import dataclass, field


@dataclass
class ResultadoPropagacion:

    red_id: str

    iteraciones: int

    valores_nodos: dict

    convergido: bool

    error: str | None = None


@dataclass
class EstadoSimulacion:

    fase: str = "inactivo"

    paso_actual: int = 0

    historial: list = field(default_factory=list)