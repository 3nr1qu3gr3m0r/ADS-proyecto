"""
EPiC Engine — Motor de propagación evidencial.
"""
from __future__ import annotations
from collections import deque
import time

from motor.dominio.modelos import Variable, Connective, EPiCModel, PropagationState

from motor.algoritmos.constantes import (
    N, T, F, B,
    VALUE_NAMES, NAME_TO_VALUE,
    future_admissible, min_surviving
)

from motor.algoritmos.tablas import NEG_TABLE, IMP_TABLE, AND_TABLE, OR_TABLE

ALL_VALUES = [N, T, F, B]


def _name(v):
    return VALUE_NAMES.get(v, "?")

def _set_name(s: set) -> str:
    if not s:
        return "{}"
    return "{" + ", ".join(sorted(_name(v) for v in s)) + "}"

def _effective(avail: set) -> frozenset:
    mins = min_surviving(avail)
    if not mins:
        return N
    return next(iter(mins)) if len(mins) == 1 else B

def _has_pos(v): return 1 in v
def _has_neg(v): return 0 in v


class _EngineState:
    def __init__(self, model: EPiCModel):
        self.available: dict[str, set] = {}
        self.fixed: set[str] = set()

        for var in model.variables:
            if var.is_premise:
                self.available[var.id] = {var.current_value}
                self.fixed.add(var.id)
            else:
                self.available[var.id] = future_admissible(var.current_value)

        self.conn_index: dict[str, list[str]] = {v.id: [] for v in model.variables}
        for conn in model.connectives:
            for vid in conn.input_ids:
                if vid in self.conn_index:
                    self.conn_index[vid].append(conn.id)
            if conn.output_id in self.conn_index:
                self.conn_index[conn.output_id].append(conn.id)

        self.conn_map = {c.id: c for c in model.connectives}
        self.var_map  = {v.id: v for v in model.variables}

        self.trace: list[dict] = []
        self.current_iteration: int = 0

    def effective(self, vid: str) -> frozenset:
        return _effective(self.available[vid])

    def restrict(self, vid: str, allowed: set) -> bool:
        if vid in self.fixed:
            return False
        cur = self.available[vid]
        nxt = cur & allowed
        if not nxt:
            nxt = {B}
        if nxt != cur:
            self.available[vid] = nxt
            return True
        return False

    def _record(self, conn_id: str, operation: str,
                before: dict, after: dict, details: str):
        self.trace.append({
            "iteration": self.current_iteration,
            "connective": conn_id,
            "operation":  operation,
            "before":     before,
            "after":      after,
            "details":    details,
        })


def _restrict_negation(state: _EngineState, conn_id: str) -> list[str]:
    conn = state.conn_map[conn_id]
    x_id, z_id = conn.input_ids[0], conn.output_id
    x_name = state.var_map[x_id].name
    z_name = state.var_map[z_id].name
    changed = []

    before = {
        x_name: _set_name(state.available[x_id]),
        z_name: _set_name(state.available[z_id]),
    }

    compat_x = {x for x in ALL_VALUES if NEG_TABLE[x] in state.available[z_id]}
    if state.restrict(x_id, compat_x): changed.append(x_id)

    compat_z = {NEG_TABLE[x] for x in state.available[x_id]}
    if state.restrict(z_id, compat_z): changed.append(z_id)

    after = {
        x_name: _set_name(state.available[x_id]),
        z_name: _set_name(state.available[z_id]),
    }

    if changed:
        state._record(
            conn_id=conn_id,
            operation="negation",
            before=before,
            after=after,
            details=(
                f"Negación: {z_name} = ¬{x_name}  |  "
                f"Cambiaron: {[state.var_map[v].name for v in changed]}"
            ),
        )

    return changed


def _restrict_implication(state: _EngineState, conn_id: str) -> list[str]:
    conn = state.conn_map[conn_id]
    x_id, y_id, z_id = conn.input_ids[0], conn.input_ids[1], conn.output_id
    x_name = state.var_map[x_id].name
    y_name = state.var_map[y_id].name
    z_name = state.var_map[z_id].name
    changed = []

    before = {
        x_name: _set_name(state.available[x_id]),
        y_name: _set_name(state.available[y_id]),
        z_name: _set_name(state.available[z_id]),
    }

    z_avail = state.available[z_id]
    x_eff   = state.effective(x_id)
    y_eff   = state.effective(y_id)

    rules_applied = []

    if _has_pos(x_eff):
        compat_y = {y for y in ALL_VALUES if IMP_TABLE.get((x_eff, y)) in z_avail}
        if state.restrict(y_id, compat_y):
            changed.append(y_id)
            rules_applied.append(f"UI+ ({x_name}={_name(x_eff)} → restringe {y_name})")

    if _has_neg(y_eff):
        compat_x = {x for x in ALL_VALUES if IMP_TABLE.get((x, y_eff)) in z_avail}
        if state.restrict(x_id, compat_x):
            changed.append(x_id)
            rules_applied.append(f"UI- ({y_name}={_name(y_eff)} → restringe {x_name})")

    new_z = {IMP_TABLE[(x, y)]
             for x in state.available[x_id]
             for y in state.available[y_id]}
    if state.restrict(z_id, new_z):
        changed.append(z_id)
        rules_applied.append(f"X×Y→Z (restringe {z_name})")

    after = {
        x_name: _set_name(state.available[x_id]),
        y_name: _set_name(state.available[y_id]),
        z_name: _set_name(state.available[z_id]),
    }

    if changed:
        state._record(
            conn_id=conn_id,
            operation="implication",
            before=before,
            after=after,
            details=(
                f"Implicación: {z_name} = {x_name}→{y_name}  |  "
                f"Reglas: {'; '.join(rules_applied)}"
            ),
        )

    return changed


def _restrict_conjunction(state: _EngineState, conn_id: str) -> list[str]:
    conn = state.conn_map[conn_id]
    x_id, y_id, z_id = conn.input_ids[0], conn.input_ids[1], conn.output_id
    x_name = state.var_map[x_id].name
    y_name = state.var_map[y_id].name
    z_name = state.var_map[z_id].name
    changed = []

    before = {
        x_name: _set_name(state.available[x_id]),
        y_name: _set_name(state.available[y_id]),
        z_name: _set_name(state.available[z_id]),
    }

    z_avail = state.available[z_id]
    x_avail = state.available[x_id]
    y_avail = state.available[y_id]

    rules_applied = []

    z_pos = any(_has_pos(z) for z in z_avail)
    if z_pos:
        cx = {x for x in x_avail if _has_pos(x)}
        cy = {y for y in y_avail if _has_pos(y)}
        if cx and state.restrict(x_id, cx):
            changed.append(x_id)
            rules_applied.append(f"Z positivo → {x_name} forzado a tener bit 1")
        if cy and state.restrict(y_id, cy):
            changed.append(y_id)
            rules_applied.append(f"Z positivo → {y_name} forzado a tener bit 1")

    cx2 = {x for x in state.available[x_id] for y in state.available[y_id] if AND_TABLE[(x, y)] in z_avail}
    cy2 = {y for y in state.available[y_id] for x in state.available[x_id] if AND_TABLE[(x, y)] in z_avail}
    if cx2 and state.restrict(x_id, cx2):
        changed.append(x_id)
        rules_applied.append(f"Tabla AND restringe {x_name}")
    if cy2 and state.restrict(y_id, cy2):
        changed.append(y_id)
        rules_applied.append(f"Tabla AND restringe {y_name}")

    new_z = {AND_TABLE[(x, y)]
             for x in state.available[x_id]
             for y in state.available[y_id]}
    if state.restrict(z_id, new_z):
        changed.append(z_id)
        rules_applied.append(f"X×Y→Z restringe {z_name}")

    after = {
        x_name: _set_name(state.available[x_id]),
        y_name: _set_name(state.available[y_id]),
        z_name: _set_name(state.available[z_id]),
    }

    if changed:
        state._record(
            conn_id=conn_id,
            operation="conjunction",
            before=before,
            after=after,
            details=(
                f"Conjunción: {z_name} = {x_name}∧{y_name}  |  "
                f"Reglas: {'; '.join(rules_applied)}"
            ),
        )

    return changed


def _restrict_disjunction(state: _EngineState, conn_id: str) -> list[str]:
    conn = state.conn_map[conn_id]
    x_id, y_id, z_id = conn.input_ids[0], conn.input_ids[1], conn.output_id
    x_name = state.var_map[x_id].name
    y_name = state.var_map[y_id].name
    z_name = state.var_map[z_id].name
    changed = []

    before = {
        x_name: _set_name(state.available[x_id]),
        y_name: _set_name(state.available[y_id]),
        z_name: _set_name(state.available[z_id]),
    }

    z_avail = state.available[z_id]
    x_avail = state.available[x_id]
    y_avail = state.available[y_id]

    rules_applied = []

    z_neg = any(_has_neg(z) for z in z_avail)
    if z_neg:
        cx = {x for x in x_avail if _has_neg(x)}
        cy = {y for y in y_avail if _has_neg(y)}
        if cx and state.restrict(x_id, cx):
            changed.append(x_id)
            rules_applied.append(f"Z negativo → {x_name} forzado a tener bit 0")
        if cy and state.restrict(y_id, cy):
            changed.append(y_id)
            rules_applied.append(f"Z negativo → {y_name} forzado a tener bit 0")

    cx2 = {x for x in state.available[x_id] for y in state.available[y_id] if OR_TABLE[(x, y)] in z_avail}
    cy2 = {y for y in state.available[y_id] for x in state.available[x_id] if OR_TABLE[(x, y)] in z_avail}
    if cx2 and state.restrict(x_id, cx2):
        changed.append(x_id)
        rules_applied.append(f"Tabla OR restringe {x_name}")
    if cy2 and state.restrict(y_id, cy2):
        changed.append(y_id)
        rules_applied.append(f"Tabla OR restringe {y_name}")

    new_z = {OR_TABLE[(x, y)]
             for x in state.available[x_id]
             for y in state.available[y_id]}
    if state.restrict(z_id, new_z):
        changed.append(z_id)
        rules_applied.append(f"X×Y→Z restringe {z_name}")

    after = {
        x_name: _set_name(state.available[x_id]),
        y_name: _set_name(state.available[y_id]),
        z_name: _set_name(state.available[z_id]),
    }

    if changed:
        state._record(
            conn_id=conn_id,
            operation="disjunction",
            before=before,
            after=after,
            details=(
                f"Disyunción: {z_name} = {x_name}∨{y_name}  |  "
                f"Reglas: {'; '.join(rules_applied)}"
            ),
        )

    return changed


def _apply_connective(state: _EngineState, conn_id: str) -> list[str]:
    ctype = state.conn_map[conn_id].type
    if ctype == "negation":    return _restrict_negation(state, conn_id)
    if ctype == "implication": return _restrict_implication(state, conn_id)
    if ctype == "conjunction": return _restrict_conjunction(state, conn_id)
    if ctype == "disjunction": return _restrict_disjunction(state, conn_id)
    return []


def print_trace(model: EPiCModel, ps: PropagationState, state: _EngineState):
    W = 80

    print("\n" + "=" * W)
    print("  VARIABLES DEL MODELO")
    print("=" * W)
    print(f"  {'ID':<12} {'Nombre':<20} {'Valor inicial':<15} {'Premisa'}")
    print("-" * W)
    for v in model.variables:
        premisa = "✓ PREMISA" if v.is_premise else ""
        print(f"  {v.id:<12} {v.name:<20} {VALUE_NAMES[v.initial_value]:<15} {premisa}")

    print("\n" + "=" * W)
    print("  CONECTIVOS")
    print("=" * W)
    print(f"  {'ID':<10} {'Tipo':<15} {'Entradas':<30} {'Salida'}")
    print("-" * W)
    for c in model.connectives:
        print(f"  {c.id:<10} {c.type:<15} {str(c.input_ids):<30} {c.output_id}")

    print("\n" + "=" * W)
    print("  TRAZA DE PROPAGACIÓN  (solo pasos con cambios)")
    print("=" * W)

    if not state.trace:
        print("  (sin cambios registrados)")
    else:
        for i, step in enumerate(state.trace, 1):
            conn   = model.connectives
            c_obj  = next((c for c in conn if c.id == step["connective"]), None)
            c_label = f"{step['connective']} ({step['operation']})" if c_obj else step["connective"]

            print(f"\n  ── Paso {i}  |  Iteración {step['iteration']}  |  {c_label}")
            print(f"     {step['details']}")
            print(f"     {'Variable':<20} {'Antes':<20} {'Después'}")
            print(f"     {'-'*55}")
            all_keys = set(step["before"]) | set(step["after"])
            for k in sorted(all_keys):
                b = step["before"].get(k, "-")
                a = step["after"].get(k, "-")
                cambio = " ◄" if b != a else ""
                print(f"     {k:<20} {b:<20} {a}{cambio}")

    print("\n" + "=" * W)
    print(f"  RESULTADO FINAL  (estable={ps.stable}, iteraciones={ps.iteration})")
    print("=" * W)
    print(f"  {'Nombre':<20} {'Inicial':<10} {'Final':<10} {'Premisa'}")
    print("-" * W)
    for v in model.variables:
        premisa = "✓" if v.is_premise else ""
        cambio  = " ◄ inferido" if not v.is_premise and v.current_value != v.initial_value else ""
        print(f"  {v.name:<20} {VALUE_NAMES[v.initial_value]:<10} {VALUE_NAMES[v.current_value]:<10} {premisa}{cambio}")
    print("=" * W + "\n")


class EPiCEngine:
    """Motor de propagación evidencial EPiC."""

    def __init__(self, max_iterations: int = 500):
        self.max_iterations = max_iterations

    def run(self, model: EPiCModel,
            verbose: bool = False) -> PropagationState:
        if not hasattr(model, 'propagation_state') or model.propagation_state is None:
            ps = PropagationState()
        else:
            ps = model.propagation_state

        ps.status = "running"
        ps.iteration = 0
        ps.updated_variable_ids = []
        ps.history = []

        state   = _EngineState(model)
        pending = deque(c.id for c in model.connectives)
        in_q    = {c.id for c in model.connectives}

        stable = False
        for iteration in range(self.max_iterations):
            state.current_iteration = iteration
            ps.iteration = iteration
            if not pending:
                stable = True
                break

            conn_id = pending.popleft()
            in_q.discard(conn_id)
            changed = _apply_connective(state, conn_id)

            for vid in changed:
                if vid not in ps.updated_variable_ids:
                    ps.updated_variable_ids.append(vid)
                ps.history.append({
                    "iteration": iteration,
                    "variable_id": vid,
                    "available": {_name(v) for v in state.available[vid]},
                    "effective": _name(state.effective(vid)),
                    "timestamp": time.time(),
                })
                for cid in state.conn_index.get(vid, []):
                    if cid not in in_q:
                        pending.append(cid)
                        in_q.add(cid)

        for var in model.variables:
            var.current_value = state.effective(var.id)

        ps.stable = stable
        ps.status = "stable" if stable else "error"

        ps._state = state

        if verbose:
            print_trace(model, ps, state)

        return ps

    def set_evidence(self, model: EPiCModel, variable_id: str,
                     value: frozenset, is_premise: bool = True):
        var = next((v for v in model.variables if v.id == variable_id), None)
        if var is None:
            raise ValueError(f"Variable '{variable_id}' no encontrada.")
        var.initial_value = value
        var.current_value = value
        var.is_premise = is_premise

    def reset(self, model: EPiCModel):
        for var in model.variables:
            var.reset()
        model.propagation_state = PropagationState()

    def get_summary(self, model: EPiCModel) -> dict:
        return {
            var.id: {
                "name":      var.name,
                "initial":   _name(var.initial_value),
                "current":   _name(var.current_value),
                "is_premise": var.is_premise,
            }
            for var in model.variables
        }


def build_test_result(model: EPiCModel, ps: PropagationState, description: str, test_name: str) -> dict:
    variables = []
    for var in model.variables:
        var_dict = {
            "id": var.id,
            "name": var.name,
            "initial_value": VALUE_NAMES[var.initial_value],
            "current_value": VALUE_NAMES[var.current_value],
            "is_premise": var.is_premise
        }
        variables.append(var_dict)

    connectives = []
    for conn in model.connectives:
        conn_dict = {
            "id": conn.id,
            "type": conn.type,
            "inputs": conn.input_ids,
            "output": conn.output_id
        }
        connectives.append(conn_dict)

    trace = []
    if hasattr(ps, '_state') and hasattr(ps._state, 'trace'):
        for step in ps._state.trace:
            trace_step = {
                "iteration": step.get("iteration", -1),
                "connective": step.get("connective", ""),
                "operation": step.get("operation", ""),
                "details": step.get("details", ""),
                "before": step.get("before", {}),
                "after": step.get("after", {})
            }
            trace.append(trace_step)

    result = {
        "test_name": test_name,
        "description": description,
        "result": {
            "stable": ps.stable,
            "iterations": ps.iteration if hasattr(ps, 'iteration') else len(trace),
            "status": ps.status if hasattr(ps, 'status') else ("stable" if ps.stable else "error")
        },
        "variables": variables,
        "connectives": connectives,
        "trace": trace
    }

    return result
