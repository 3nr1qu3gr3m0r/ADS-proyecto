# ADS — EPiC Playground
### Sistema de Simulación por Propagación de Tablas de Verdad (Belnap 4 valores)

---

## Descripción general

EPiC Playground es un sistema web para construir, editar y simular redes lógicas basadas en la **lógica evidencial de cuatro valores de Belnap**. El usuario dibuja una red de nodos en el editor visual, el Motor propaga los valores consultando tablas de verdad, y el Simulador expone el historial paso a paso para que el Visualizador lo muestre de forma animada.

El sistema está dividido en cinco componentes desacoplados que se comunican a través de contratos definidos en el dominio compartido:

```
Editor (frontend)  →  Simulador (backend)  →  Motor (backend)
                             ↓
                       Visualizador (frontend)
                             ↓
                     Compartido (backend + frontend)
```

**Stack:** React 18 + TypeScript + Vite (frontend) · FastAPI + Python 3.11 (backend)

---

## Lógica de Belnap — 4 valores evidenciales

A diferencia de la lógica booleana (solo True/False), Belnap añade dos valores para representar falta de información y contradicción de fuentes:

| Símbolo | Nombre | Significado |
|---------|--------|-------------|
| **T** | Verdadero | Solo hay evidencia **positiva** |
| **F** | Falso | Solo hay evidencia **negativa** |
| **B** | Ambos | Hay evidencia positiva **y** negativa (contradicción) |
| **N** | Ninguno | **Sin evidencia** en ningún sentido (indeterminado) |

### Modelo bitpair

Cada valor se representa internamente como dos bits: `(bit_negativo, bit_positivo)`:

```
N = (0,0)   F = (1,0)   T = (0,1)   B = (1,1)
```

Las operaciones se derivan de este modelo, garantizando consistencia matemática.

---

## Tablas de verdad completas

### NOT — 1 entrada obligatoria

| Entrada | Resultado |
|---------|-----------|
| T | **F** |
| F | **T** |
| B | **B** |
| N | **N** |

Derivación: `NEG(a) = swap(bits)` → `NEG(0,1) = (1,0) = F`

---

### AND — 2 o más entradas

`AND(a,b) = (max(neg), min(pos))` — tan fuerte como la entrada **más débil**

| AND | N | T | F | B |
|-----|---|---|---|---|
| **N** | N | N | F | F |
| **T** | N | T | F | B |
| **F** | F | F | F | F |
| **B** | F | B | F | B |

Casos clave: `T∧T=T`, `T∧F=F`, `B∧T=B` (la contradicción se contagia), `N∧T=N` (la duda frena).

---

### OR — 2 o más entradas

`OR(a,b) = (min(neg), max(pos))` — tan fuerte como la entrada **más fuerte**

| OR | N | T | F | B |
|----|---|---|---|---|
| **N** | N | T | N | T |
| **T** | T | T | T | T |
| **F** | N | T | F | B |
| **B** | T | T | B | B |

Casos clave: `T∨F=T`, `F∨F=F`, `N∨T=T` (evidencia positiva gana), `B∨F=B`.

---

### XOR — 2 o más entradas

`XOR(a,b) = OR(AND(a,NEG(b)), AND(NEG(a),b))` — verdadero si **exactamente una** entrada es T

| XOR | N | T | F | B |
|-----|---|---|---|---|
| **N** | N | N | N | F |
| **T** | N | F | T | B |
| **F** | N | T | F | B |
| **B** | F | B | B | B |

Casos clave: `T⊕T=F` (exclusivo), `T⊕F=T`, `B⊕x=B` (contradicción siempre se propaga).

---

### IMP — exactamente 2 entradas (antecedente → consecuente)

`IMP(a,b) = OR(NEG(a), b)` — implicación material a → b

| IMP (a→b) | N | T | F | B |
|-----------|---|---|---|---|
| **N** | N | T | N | T |
| **T** | N | T | F | B |
| **F** | T | T | T | T |
| **B** | T | T | B | B |

Casos clásicos: `T→T=T`, `T→F=F`, `F→T=T`, `F→F=T`.

> **Orden de conexión en IMP:** la primera arista conectada es el antecedente (a), la segunda es el consecuente (b). El formulario muestra un aviso al seleccionar un nodo IMP como destino.

---

## Tipos de nodo

| Tipo | Descripción | Entradas | Valor |
|------|-------------|----------|-------|
| **Premisa ★** | Hecho conocido / axioma | 0 (solo salidas) | Fijo: T, F, B o N |
| **AND** | Conjunción | 2 o más | Calculado por tabla |
| **OR** | Disyunción | 2 o más | Calculado por tabla |
| **XOR** | Disyunción exclusiva | 2 o más | Calculado por tabla |
| **NOT** | Negación | Exactamente 1 | Calculado por tabla |
| **IMP** | Implicación a→b | Exactamente 2 | Calculado por tabla |

**Regla fundamental:** las premisas solo pueden tener aristas **salientes**. Una arista que apunte a una premisa es rechazada tanto en el frontend como en el backend con el error `ENTRADA_A_PREMISA`.

---

## Distribución de equipos

| Subequipo | Integrantes | Responsabilidad principal |
|-----------|-------------|--------------------------|
| **Subequipo 1** | De La Riva Martínez Héctor Josué<br>Bernal Linares César Arturo<br>Montaño Sánchez Daniela<br>García López Andrés Adad | Editor (Frontend) |
| **Subequipo 2** | Cortés Avilez Yoshua<br>Gutiérrez López Samuel<br>Luciano Alvarado Ana Cristina<br>Pérez Montaño Sergio Patricio | Motor de cálculo (Backend) |
| **Subequipo 3** | Aldama Nava Nadir Ibrain<br>Peralta Llera Elizabeth<br>Toribio Segura Alma Jessica<br>Varillas Figueroa Enrique Uriel | Simulador (Backend) |
| **Todos** | 12 personas | Compartido · Visualizador |

> Cualquier cambio en `backend/compartido/` o `frontend/src/compartido/` requiere revisión y aprobación de los **3 subequipos** antes de hacer merge.

---

## Estructura de carpetas

```
ads-final/
│
├── backend/
│   ├── compartido/                   ← ⚠️  BASE COMÚN — todos los equipos
│   │   ├── modelos.py                → Nodo, Arista, Red, ResultadoPropagacion,
│   │   │                                EstadoSimulacion, ErrorValidacion
│   │   ├── contratos.py              → IMotorCalculo, IMotorCalculoIterativo,
│   │   │                                ISimulacion, TIPOS_OPERADOR, VALORES_BELNAP,
│   │   │                                FaseSimulacion, eventos, excepciones
│   │   ├── validadores.py            → validar_nodo(), validar_arista(), validar_red()
│   │   └── utilidades.py             → generar_id(), clamp(), formatear_resultado()
│   │
│   ├── motor/                        ← 🔴 SUBEQUIPO 2
│   │   ├── algoritmos.py             → NEG_TABLE, AND_TABLE, OR_TABLE, XOR_TABLE,
│   │   │                                IMP_TABLE, aplicar_operador(),
│   │   │                                _orden_topologico(), MotorTablas, obtener_motor()
│   │   ├── api.py                    → POST /api/v1/redes/{id}/calcular
│   │   │                                GET  /api/v1/propagaciones/{id}
│   │   └── test_motor.py             → Tests de tablas + propagación (sin mocks)
│   │
│   ├── simulador/                    ← 🔵 SUBEQUIPO 3
│   │   ├── estado.py                 → GestorEstadoSimulacion (almacén en memoria)
│   │   ├── servicio.py               → SimulacionServicio (implementa ISimulacion)
│   │   ├── api.py                    → POST /api/v1/simulaciones  (+ GET/PUT)
│   │   └── test_simulador.py         → Tests con Motor mockeado
│   │
│   ├── principal.py                  → App FastAPI: monta routers + CORS
│   └── requerimientos.txt            → fastapi, uvicorn, pydantic, pytest
│
└── frontend/
    ├── index.html
    ├── package.json                  → react 18, vite 6, typescript 5, tailwind 3
    ├── vite.config.ts
    ├── tsconfig.json
    ├── tailwind.config.js
    └── src/
        ├── main.tsx                  → ReactDOM.createRoot
        ├── App.tsx                   → ⚠️  Estado global, simulación, layout
        ├── index.css                 → Variables CSS + animación de flechas
        │
        ├── compartido/               ← ⚠️  BASE COMÚN — todos los equipos
        │   ├── tipos.ts              → Nodo, Arista, Red, ValorBelnap, TipoNodo,
        │   │                            ResultadoPropagacion, EstadoSimulacion
        │   ├── api.ts                → calcularRed(), iniciarSimulacion(),
        │   │                            pausarSimulacion(), avanzarPaso(), retrocederPaso()
        │   └── constantes.ts         → COLOR_BELNAP, DESC_BELNAP, PALETA, PRESETS
        │
        ├── editor/                   ← 🟢 SUBEQUIPO 1
        │   ├── CanvasEditor.tsx      → SVG con drag-and-drop + colores T/F/B/N + flechas
        │   ├── FormularioNodo.tsx    → Formulario: premisa (valor T/F/B/N) vs operador
        │   └── FormularioArista.tsx  → Conexión entre nodos (valida premisas sin entrada)
        │
        └── visualizador/             ← ⚠️  TODOS — componentes compartidos
            ├── ControlesSimulacion.tsx → Play / Pausar / ⏮ ⏭ / Nueva simulación
            └── PanelResultados.tsx   → Tarjetas de valor por nodo + leyenda Belnap
```

---

## Contratos de datos (JSON)

### Nodo premisa

```json
{
  "id": "nodo-001",
  "etiqueta": "P",
  "tipo": "premisa",
  "propiedades": { "valor": "T" },
  "posicion": { "x": 120, "y": 340 }
}
```

### Nodo operador

```json
{
  "id": "nodo-002",
  "etiqueta": "P ∧ Q",
  "tipo": "AND",
  "propiedades": {},
  "posicion": { "x": 400, "y": 200 }
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `string` | Formato obligatorio: `"nodo-*"` |
| `etiqueta` | `string` | Nombre visible (acepta: ¬ ∧ ∨ → ↔ ∴ ⊥ ⊤ ∀ ∃) |
| `tipo` | `"premisa" \| "AND" \| "OR" \| "XOR" \| "NOT" \| "IMP"` | Tipo de nodo |
| `propiedades.valor` | `"T" \| "F" \| "B" \| "N"` | Solo en premisas |
| `posicion` | `{ x, y }` | Coordenadas en el canvas |

### Arista

```json
{
  "id": "arista-001",
  "idOrigen": "nodo-001",
  "idDestino": "nodo-002",
  "peso": 1.0,
  "metadatos": {}
}
```

> `idDestino` **no puede ser una premisa**.

### ResultadoPropagacion

```json
{
  "redId": "red-001",
  "iteraciones": 1,
  "valoresNodos": {
    "nodo-P":  "T",
    "nodo-PQ": "T",
    "nodo-A":  "T",
    "nodo-Q":  "T"
  },
  "convergido": true,
  "error": null
}
```

`iteraciones: 0` = estado inicial antes de propagar. `convergido: true` = resultado final estable.

### EstadoSimulacion

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "fase": "completado",
  "pasoActual": 2,
  "historial": [
    { "iteraciones": 0, "valoresNodos": {"nodo-A":"N","nodo-Q":"N"}, "convergido": false },
    { "iteraciones": 1, "valoresNodos": {"nodo-A":"T","nodo-Q":"T"}, "convergido": false },
    { "iteraciones": 2, "valoresNodos": {"nodo-A":"T","nodo-Q":"T"}, "convergido": true }
  ]
}
```

---

## Contrato de API REST

| Método | Ruta | Cuerpo | Respuesta | Descripción |
|--------|------|--------|-----------|-------------|
| `POST` | `/api/v1/redes/{id}/calcular` | `Red` | `ResultadoPropagacion` | Resultado final directo (sin historial) |
| `GET` | `/api/v1/propagaciones/{id}` | — | `ResultadoPropagacion` | Último resultado calculado para esa red |
| `POST` | `/api/v1/simulaciones` | `{ red: Red }` | `EstadoSimulacion` 201 | Inicia simulación; devuelve historial completo |
| `GET` | `/api/v1/simulaciones/{id}` | — | `EstadoSimulacion` | Consulta estado actual |
| `PUT` | `/api/v1/simulaciones/{id}/pausar` | — | `{id, fase}` | Cambia fase a `"pausado"` |
| `PUT` | `/api/v1/simulaciones/{id}/reanudar` | — | `{id, fase}` | Cambia fase a `"corriendo"` |
| `PUT` | `/api/v1/simulaciones/{id}/avanzar` | — | `SalidaPaso` | Incrementa `pasoActual` en servidor |
| `PUT` | `/api/v1/simulaciones/{id}/retroceder` | — | `SalidaPaso` | Decrementa `pasoActual` en servidor |

> El frontend navega el historial **localmente** (ya tiene todos los pasos tras el POST inicial) sin llamar a `avanzar/retroceder` en cada clic.

---

## Interfaces del backend

### `IMotorCalculo`

```python
class IMotorCalculo(ABC):
    @abstractmethod
    def calcular(self, red: Red) -> ResultadoPropagacion: ...
```

### `IMotorCalculoIterativo(IMotorCalculo)`

```python
class IMotorCalculoIterativo(IMotorCalculo):
    @abstractmethod
    def calcular_pasos(self, red: Red) -> list[ResultadoPropagacion]: ...
```

El Simulador depende de esta interfaz (ISP). Quien solo necesite el resultado final puede depender solo de `IMotorCalculo`.

### `ISimulacion`

```python
class ISimulacion(ABC):
    @abstractmethod
    def iniciar(self, red: Red) -> str: ...   # retorna el ID de simulación
    @abstractmethod
    def pausar(self) -> None: ...
    @abstractmethod
    def reanudar(self) -> None: ...
    @abstractmethod
    def paso(self) -> None: ...
```

---

## Cómo funciona el Motor (solo tablas)

El Motor no usa ningún algoritmo numérico. Solo tablas de verdad en el orden correcto:

**1. Ordenamiento topológico (algoritmo de Kahn)**

Los nodos se ordenan de modo que cuando el Motor procesa un nodo, todos sus predecesores ya tienen su valor actualizado en esta misma pasada.

```
Premisas (0 entradas) → nivel 1 (dependen de premisas) → nivel 2 → ...
```

**2. Una sola pasada consultando las tablas**

Para cada nodo operador, en orden topológico:
1. Leer los valores **ya actualizados** de sus nodos de entrada
2. Consultar `AND_TABLE`, `OR_TABLE`, `XOR_TABLE`, `NOT_TABLE` o `IMP_TABLE`
3. Guardar el nuevo valor

**3. Historial generado**

| Paso | `iteraciones` | Descripción |
|------|---------------|-------------|
| 0 | 0 | Estado inicial: premisas con su valor, operadores en N |
| 1 | 1 | Después de la primera pasada por las tablas |
| 2+ | 2+ | Solo si hay ciclos en la red |
| Último | n | Primer paso donde `convergido = true` |

Para redes sin ciclos (el caso habitual), el resultado correcto aparece en el **paso 1**. El frontend muestra el **último paso** por defecto.

---

## Principios SOLID aplicados

| Principio | Aplicación |
|-----------|-----------|
| **S** — Responsabilidad única | `algoritmos.py` solo consulta tablas. `estado.py` solo persiste. `servicio.py` solo orquesta. Cada componente React tiene una sola razón de cambio. |
| **O** — Abierto/cerrado | Agregar una nueva tabla (NAND, NOR...) solo requiere tocar `algoritmos.py` y `contratos.py`, sin modificar el Simulador ni la API. |
| **L** — Sustitución de Liskov | `MotorTablas` implementa `IMotorCalculoIterativo`. Cualquier otra implementación es intercambiable sin modificar el Simulador. |
| **I** — Segregación de interfaces | `IMotorCalculo` (solo `calcular`) para quien solo quiere el resultado final. `IMotorCalculoIterativo` (agrega `calcular_pasos`) para quien necesita el historial. |
| **D** — Inversión de dependencias | `SimulacionServicio` recibe `FabricaMotor: Callable[[], IMotorCalculoIterativo]` por constructor; nunca importa `MotorTablas` directamente. La dependencia concreta se inyecta en `simulador/api.py` (composition root). |

---

## Flujo de datos completo

```
[CanvasEditor.tsx / FormularioNodo.tsx / FormularioArista.tsx]
  El usuario dibuja la red
          │
          ▼
[App.tsx]
  POST /api/v1/simulaciones   →   { red: { id, nodos, aristas } }
          │
          ▼
[simulador/api.py]
  JSON → Red (Python)
  SimulacionServicio.iniciar(red)
          │
          ▼
[simulador/servicio.py]
  1. validar_red(red)                           ← rechaza si hay errores estructurales
  2. motor = fabrica_motor()                    ← MotorTablas (DIP)
  3. pasos = motor.calcular_pasos(red)          ← historial completo
  4. gestor.establecer_historial(sim_id, pasos)
  5. retorna EstadoSimulacion con todo el historial
          │
          ▼
[motor/algoritmos.py — MotorTablas]
  1. _orden_topologico(red)    →  nodos en orden de dependencia
  2. valores = { premisas: su_valor, operadores: "N" }
  3. Por cada pasada:
       Para cada nodo en orden topológico:
           vals = [nuevos[origen] for origen in entradas[nodo]]
           nuevos[nodo] = TABLA[(vals[0], vals[1], ...)]
     Si ningún valor cambió → convergido=True, termina
  4. Retorna lista de ResultadoPropagacion (paso 0 = estado inicial)
          │
          ▼
[App.tsx — respuesta recibida]
  setSimulacion(res)
  setPasoVisible(res.historial.length - 1)    ← muestra resultado final por defecto
          │
          ▼
[CanvasEditor.tsx + PanelResultados.tsx]
  Nodos coloreados por T/F/B/N del paso visible
  Flechas animadas con el color del nodo origen
  Barra de puntos para saltar a cualquier iteración
```

---

## Validaciones del sistema

| Código | Causa |
|--------|-------|
| `NODO_FORMATO_INVALIDO` | ID no sigue el formato `"nodo-*"` |
| `NODO_DUPLICADO` | Dos nodos con el mismo ID |
| `NODO_SIN_ETIQUETA` | Etiqueta vacía |
| `TIPO_INVALIDO` | Tipo no es `premisa`, `AND`, `OR`, `XOR`, `NOT` ni `IMP` |
| `VALOR_BELNAP_INVALIDO` | Valor de premisa no es T, F, B ni N |
| `ARISTA_FORMATO_INVALIDO` | ID no sigue el formato `"arista-*"` |
| `ENTRADA_A_PREMISA` | Una arista apunta a una premisa |
| `AUTO_LOOP` | Un nodo conectado a sí mismo |
| `NOT_ENTRADAS_INVALIDAS` | Nodo NOT sin exactamente 1 entrada |
| `IMP_ENTRADAS_INVALIDAS` | Nodo IMP sin exactamente 2 entradas |
| `ORIGEN_INEXISTENTE` | La arista referencia un nodo que no existe |
| `GRAFO_VACIO` | La red no tiene nodos |

---

## Cómo ejecutar (desde cero)

### Requisitos previos

| Herramienta | Versión mínima | Verificar |
|-------------|----------------|-----------|
| Python | 3.11 | `python --version` |
| Node.js | 18 | `node --version` |
| npm | 9 | `npm --version` |

Si alguno no está instalado:
- **Python** → https://www.python.org/downloads/ (marcar "Add to PATH" en Windows)
- **Node.js** → https://nodejs.org (versión LTS)

### Paso 1 — Obtener el proyecto

```bash
git clone <url-del-repositorio>
cd ads-final
# o descomprimir el ZIP y entrar a la carpeta
```

### Paso 2 — Backend

```bash
cd ads-final/backend
pip install -r requerimientos.txt
uvicorn principal:app --reload --port 8000
```

Verificar: `http://localhost:8000/docs` → Swagger con todos los endpoints.

### Paso 3 — Frontend (nueva terminal)

```bash
cd ads-final/frontend
npm install       # solo la primera vez
npm run dev
```

Abrir: `http://localhost:5173`

### Resumen diario

```bash
# Terminal 1
cd ads-final/backend && uvicorn principal:app --reload --port 8000

# Terminal 2
cd ads-final/frontend && npm run dev
```

### Pruebas

```bash
cd ads-final/backend
pytest motor/test_motor.py simulador/test_simulador.py -v
# → 42 tests en verde
```

### Problemas frecuentes

| Error | Solución |
|-------|---------|
| `No module named 'fastapi'` | `pip install -r requerimientos.txt` |
| `pip: command not found` | Reinstalar Python marcando "Add to PATH" |
| `Failed to connect to port 8000` | Verificar que la Terminal 1 esté activa |
| `npm: command not found` | Instalar Node.js desde nodejs.org |
| Puerto 8000 ocupado | `uvicorn principal:app --port 8001` y actualizar `VITE_API_URL` en `.env.ejemplo` |

---

## Cómo usar el editor

1. **Agregar nodo** — elegir tipo:
   - **Premisa ★** → seleccionar valor fijo T/F/B/N con los botones de color
   - **Operador ⊕** → elegir AND, OR, XOR, NOT o IMP
   - La barra de símbolos permite insertar ¬ ∧ ∨ → ↔ ∴ ⊥ ⊤ ∀ ∃ en la etiqueta

2. **Conectar nodos** — seleccionar origen y destino. Las premisas solo pueden ser origen. Para IMP: conectar primero el antecedente, luego el consecuente.

3. **Presets** — cargar desde el header: `modus-ponens`, `contradiccion`, `xor`.

4. **Simular** — clic en "▶ Simular red". Por defecto muestra el resultado final (convergido). Los nodos se colorean por T/F/B/N y las flechas se animan.

5. **Navegar** — usar los círculos numerados bajo el canvas o los botones ⏮/⏭ para ver cómo se propagaron los valores iteración por iteración. El paso 0 es el estado inicial (operadores en N).

6. **Editar** — arrastrar nodos, doble clic para eliminar, clic en arista para eliminarla.

---

## Paleta de colores

| Color | Valor | Significado |
|-------|-------|-------------|
| 🟢 Verde `#22c55e` | T | Verdadero |
| 🔴 Rojo `#ef4444` | F | Falso |
| 🟠 Naranja `#f59e0b` | B | Contradicción |
| ⚫ Gris `#6b7280` | N | Sin evidencia |

---

## Flujo de trabajo con Git

### Ramas

```
main     → producción; solo merge con revisión de los 3 subequipos
develop  → integración; aquí llegan los PR de trabajo
```

### Nomenclatura de ramas

```
feature/editor-formulario-imp
feature/motor-tabla-imp
feature/simulador-historial-paso0
fix/canvas-drag-stale-closure
docs/readme-v3
```

### Formato de commits

```
agrega IMP_TABLE en motor/algoritmos.py
corrige bug de stale-closure en CanvasEditor.tsx
extrae GestorEstadoSimulacion a simulador/estado.py
rechaza aristas entrantes a premisas en validadores.py
```

### Reglas de merge

- Todo PR necesita **mínimo 1 aprobación de otro subequipo**
- Cambios en `compartido/` → **1 aprobación de cada subequipo** (3 en total)
- No hacer merge si `pytest` no está en verde

---

## Convenciones de código

### Backend (Python)

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| Variables y funciones | `snake_case` | `calcular_pasos`, `red_id` |
| Clases | `PascalCase` | `MotorTablas`, `SimulacionServicio` |
| Constantes | `SCREAMING_SNAKE_CASE` | `AND_TABLE`, `MAX_ITERACIONES` |
| Atributos privados | `_snake_case` | `self._estados` |
| Interfaces | `I` + `PascalCase` | `IMotorCalculo`, `ISimulacion` |
| Archivos | `snake_case.py` | `algoritmos.py`, `estado.py` |

### Frontend (TypeScript / React)

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| Componentes | `PascalCase.tsx` | `CanvasEditor.tsx` |
| Hooks | `use` + `camelCase` | `useState`, `useCallback` |
| Variables | `camelCase` | `valoresNodos`, `pasoVisible` |
| Constantes globales | `SCREAMING_SNAKE_CASE` | `COLOR_BELNAP`, `AND_TABLE` |
| Tipos | `PascalCase` | `ValorBelnap`, `NodoConValor` |

---

## Plan de 10 semanas

| Semanas | Todos | Subequipo 1 — Editor | Subequipo 2 — Motor | Subequipo 3 — Simulador |
|---------|-------|----------------------|---------------------|--------------------------|
| 1–2 | Acordar `compartido/`: tipos, tablas, contratos | Setup Vite + canvas base | Setup FastAPI + tablas iniciales | Definir API de simulación |
| 3–5 | Revisiones cruzadas de PRs | Editor: premisas y operadores | Tablas completas + orden topológico | Servicio + GestorEstado |
| 6–8 | Integración progresiva | Conectar editor con API real | Validaciones + pruebas | Historial paso a paso |
| 9 | Visualizador conjunto | CanvasEditor coloreado + animaciones | Exportar historial al Simulador | Navegación de iteraciones |
| 10 | Pruebas de integración y demo final | — | — | — |
