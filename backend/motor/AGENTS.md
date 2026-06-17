# AGENTS.md — Motor EPiC

## Project

Evidential propagation engine (EPiC) — 4-valued logic {N, T, F, B} using frozenset representation. FastAPI backend that accepts logical network graphs and propagates evidence bidirectionally through connectives.

## Quick start

```bash
pip install fastapi uvicorn pydantic
uvicorn motor.principal:app --reload       # dev server (port 8000)
```

## Running tests (NOT pytest)

Tests are standalone scripts with `__main__` runners, NOT pytest:

```bash
python -m motor.pruebas.test_engine                # tests 8-13
python -m motor.pruebas.test_propagacion_servicio   # tests 1-7
python -m motor.pruebas.exportar_json               # run all tests → JSON report
```

Single test: comment out the runner block and call a test function directly.

## Architecture

```
motor/principal.py           — FastAPI entrypoint
motor/dominio/modelos.py     — Domain dataclasses (Variable, Connective, etc.)
motor/api/rutas.py           — POST /api/v1/redes/{id}/calcular
motor/api/esquemas.py        — Pydantic schemas
motor/servicios/propagacion_servicio.py    — Orchestrates adapter + engine
motor/servicios/construccion_matriz.py     — JSON → EPiCModel adapter + result builder
motor/algoritmos/engine.py   — Core EPiCEngine with worklist propagation
motor/algoritmos/constantes.py — 4-valued domain {N, T, F, B}
motor/algoritmos/tablas.py                — Truth tables (NEG, IMP, AND, OR)
motor/pruebas/test_engine.py              — Tests 8-13 (chains, dilemma, medical)
motor/pruebas/test_propagacion_servicio.py — Tests 1-7 (modus ponens, tollens, etc.)
motor/pruebas/exportar_json.py            — Test result exporter
```

## API endpoint

```
POST /api/v1/redes/{id}/calcular
Body: { id, nodos, aristas, version }   (see network.json for format)
```

## Testing quirks

- Tests use `verbose=True` which prints full trace — useful for debugging but noisy.
- Tests modify `current_value` on variables in-place (no fixtures).
- Assertion errors are caught by the custom runner — use `__main__` block, not `pytest`.
- Test files add `sys.path.insert(0, ...)` at import time.

## Dependencies

- fastapi, uvicorn, pydantic (all installable via pip, no lockfile)
- Python 3.13+ (inferred from .pyc)
