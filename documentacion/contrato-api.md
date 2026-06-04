# Contrato de API REST

Todos los endpoints usan prefijo `/api/v1/`. El body siempre es JSON.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/v1/redes/{id}/calcular` | Dispara el cálculo matricial |
| `GET` | `/api/v1/propagaciones/{id}` | Obtiene un resultado guardado |
| `POST` | `/api/v1/simulaciones` | Inicia una simulación nueva |
| `GET` | `/api/v1/simulaciones/{id}` | Consulta el estado actual |
| `PUT` | `/api/v1/simulaciones/{id}/pausar` | Pausa la simulación |
| `PUT` | `/api/v1/simulaciones/{id}/avanzar` | Avanza un paso manual |

## Ejemplos

### POST /api/v1/redes/{id}/calcular

**Request body:**
```json
{
  "id": "red-001",
  "nodos": [
    { "id": "nodo-001", "tipo": "AND", "etiqueta": "A", "propiedades": {}, "posicion": { "x": 0, "y": 0 } },
    { "id": "nodo-002", "tipo": "OR", "etiqueta": "B", "propiedades": {}, "posicion": { "x": 100, "y": 0 } }
  ],
  "aristas": [
    { "id": "arista-001", "idOrigen": "nodo-001", "idDestino": "nodo-002", "peso": 1.0, "metadatos": {} }
  ],
  "version": 1
}
```

**Response (200):**
```json
{
  "redId": "red-001",
  "iteraciones": 48,
  "valoresNodos": { "nodo-001": 1.0, "nodo-002": 0.83 },
  "convergido": true,
  "error": null
}
```

### POST /api/v1/simulaciones

**Request body:**
```json
{ "red": { ... } }
```

**Response (201):**
```json
{ "id": "sim-001", "fase": "inactivo", "pasoActual": 0, "historial": [] }
```

### GET /api/v1/simulaciones/{id}

**Response (200):**
```json
{ "id": "sim-001", "fase": "corriendo", "pasoActual": 3, "historial": [] }
```