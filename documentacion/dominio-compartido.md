# Dominio Compartido — Contrato JSON

Este documento define la estructura canónica de datos del sistema.

## Tipos principales

### Nodo

```json
{
  "id": "nodo-001",
  "tipo": "AND",
  "etiqueta": "Nodo A",
  "propiedades": { "entradas": 2 },
  "posicion": { "x": 120, "y": 340 }
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `string` | Identificador único. Formato: `"nodo-{número}"` |
| `tipo` | `"AND" \| "OR" \| "NOT"` | Rol del nodo en la red |
| `etiqueta` | `string` | Nombre visible en el editor |
| `propiedades` | `objeto clave:número` | Valores específicos del dominio |
| `posicion.x` | `número` | Posición horizontal en el canvas |
| `posicion.y` | `número` | Posición vertical en el canvas |

### Arista

```json
{
  "id": "arista-001",
  "idOrigen": "nodo-001",
  "idDestino": "nodo-002",
  "peso": 0.75,
  "metadatos": { "etiqueta": "Conexión A-B" }
}
```

### Red

```json
{
  "id": "red-001",
  "nodos": [],
  "aristas": [],
  "version": 3
}
```

### ResultadoPropagacion

```json
{
  "redId": "red-001",
  "iteraciones": 48,
  "valoresNodos": { "nodo-001": 1.0, "nodo-002": 0.83 },
  "convergido": true,
  "error": null
}
```

### EstadoSimulacion

```json
{
  "fase": "corriendo",
  "pasoActual": 3,
  "historial": []
}
```

Fases: `"inactivo"`, `"corriendo"`, `"pausado"`, `"completado"`, `"error"`

## Mapeo JSON → Python

| Campo JSON | Campo Python | Notas |
|---|---|---|
| `idOrigen` | `id_origen` | snake_case en Python |
| `idDestino` | `id_destino` | |
| `redId` | `red_id` | |
| `valoresNodos` | `valores_nodos` | dict |
| `pasoActual` | `paso_actual` | |
| `nodoId` | `nodo_id` | |
| `aristaId` | `arista_id` | |

## Validaciones

- Nodos: ID formato `nodo-*`, tipo en {AND, OR, NOT}, etiqueta no vacía
- Aristas: ID formato `arista-*`, idOrigen/idDestino existen, sin self-loops
- Red: al menos 1 nodo, sin ciclos (DFS)