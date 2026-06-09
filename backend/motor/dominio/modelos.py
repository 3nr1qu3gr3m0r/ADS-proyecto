"""
Estructuras de datos del dominio EPiC.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from motor.algoritmos.constantes import N


@dataclass
class Variable:
    id: str
    name: str
    initial_value: frozenset = field(default_factory=lambda: N)
    current_value: frozenset = field(default_factory=lambda: N)
    is_premise: bool = False
    metadata: dict = field(default_factory=dict)

    def reset(self):
        self.current_value = self.initial_value


@dataclass
class Arc:
    id: str
    source_id: str
    target_id: str
    kind: str = "directed"
    metadata: dict = field(default_factory=dict)


@dataclass
class Connective:
    id: str
    type: str
    input_ids: list[str] = field(default_factory=list)
    output_id: str = ""
    matrix_id: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class Matrix:
    id: str
    connective_id: str
    values: list[list] = field(default_factory=list)

    @property
    def rows(self): return len(self.values)
    @property
    def cols(self): return len(self.values[0]) if self.values else 0


@dataclass
class PropagationState:
    iteration: int = 0
    stable: bool = False
    status: str = "idle"
    updated_variable_ids: list[str] = field(default_factory=list)
    history: list[dict] = field(default_factory=list)


@dataclass
class EPiCModel:
    id: str
    name: str = "EPiC Model"
    variables: list[Variable] = field(default_factory=list)
    arcs: list[Arc] = field(default_factory=list)
    connectives: list[Connective] = field(default_factory=list)
    matrices: list[Matrix] = field(default_factory=list)
    propagation_state: PropagationState = field(default_factory=PropagationState)
    metadata: dict = field(default_factory=dict)
