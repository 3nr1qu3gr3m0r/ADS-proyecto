# ADS — Proyecto de Simulación por Propagación Matricial

## Descripción general

Sistema web para la edición, cálculo y simulación de redes mediante propagación matricial.
Desarrollado por un equipo de 12 personas divididas en 3 subequipos durante 10 semanas.
Construido con **React** (frontend), **FastAPI/Python** (backend) y versionado con **Git**.

---

## Distribución de equipos

| Subequipo | Integrantes | Componentes a cargo |
|-----------|-------------|---------------------|
| **Subequipo 1** | 4 personas | Editor + participa en Dominio compartido y Visualizador |
| **Subequipo 2** | 4 personas | Motor de cálculo matricial + participa en Dominio compartido y Visualizador |
| **Subequipo 3** | 4 personas | Simulador + participa en Dominio compartido y Visualizador |

> **Regla de oro:** Las carpetas `compartido/` (frontend y backend) y `visualizador/` son territorio de todos.
> Cualquier cambio en ellas **requiere revisión y aprobación de los 3 subequipos** antes de hacer merge.

---

## Estructura de carpetas

```
ADS-proyecto/
├── frontend/                         → Todo lo que ve el usuario (React + TypeScript)
│   └── src/
│       ├── compartido/               → ⚠️ TODOS los equipos — base común del frontend
│       │   ├── dominio/
│       │   │   ├── tipos.ts          → Interfaces: Nodo, Arista, Red, ResultadoPropagacion
│       │   │   ├── eventos.ts        → Eventos del sistema entre componentes
│       │   │   ├── validadores.ts    → validarRed(), validarNodo(), validarArista()
│       │   │   └── constantes.ts     → MAX_NODOS, API_BASE_URL, TOLERANCIA_DEFAULT
│       │   ├── hooks/
│       │   │   ├── useRed.ts         → Estado global de la red (contexto React)
│       │   │   └── useSimulacion.ts  → Conecta con el simulador vía API
│       │   ├── api/
│       │   │   ├── simulacion.api.ts → POST /simulaciones, GET /simulaciones/:id
│       │   │   ├── propagacion.api.ts→ POST /calcular, GET /resultado/:id
│       │   │   └── cliente.http.ts   → Axios configurado con interceptores
│       │   └── utilidades.ts         → formatearValor(), generarId(), redondear()
│       │
│       ├── editor/                   → 🟢 SUBEQUIPO 1
│       │   ├── componentes/
│       │   │   ├── CanvasEditor.tsx  → Lienzo principal con drag & drop de nodos
│       │   │   ├── FormularioNodo.tsx→ Panel lateral para editar propiedades del nodo
│       │   │   ├── BarraHerramientas.tsx → Botones: agregar nodo, arista, eliminar
│       │   │   └── ConectorArista.tsx→ Línea visual e interactiva entre dos nodos
│       │   ├── hooks/
│       │   │   ├── useEditor.ts      → Maneja selección, modo edición, cursor
│       │   │   └── useHistorialEditor.ts → Undo / Redo de acciones en el canvas
│       │   ├── servicios/
│       │   │   └── editor.servicio.ts→ Lógica de negocio del editor (SOLID S)
│       │   └── PaginaEditor.tsx      → Página completa que ensambla el editor
│       │
│       ├── visualizador/             → ⚠️ TODOS los equipos construyen aquí
│       │   ├── componentes/
│       │   │   ├── GrafoVisual.tsx       → Render D3.js del grafo con mapa de calor
│       │   │   ├── PanelResultados.tsx   → Tabla de valores calculados por nodo
│       │   │   ├── ControlSimulacion.tsx → Botones play / pause / paso a paso
│       │   │   ├── GraficaConvergencia.tsx → Gráfica iteraciones vs error
│       │   │   └── LeyendaColores.tsx    → Leyenda del mapa de calor por intensidad
│       │   ├── hooks/
│       │   │   └── useVisualizador.ts    → Estado local de la vista actual
│       │   └── PaginaVisualizador.tsx    → Página que ensambla toda la visualización
│       │
│       ├── main.tsx                  → Punto de entrada de React
│       ├── App.tsx                   → Router principal y layout general
│       ├── package.json
│       ├── tsconfig.json
│       ├── vite.config.ts
│       └── .env.ejemplo              → VITE_API_URL=http://localhost:8000
│
├── backend/                          → Lógica de cálculo y simulación (Python + FastAPI)
│   ├── compartido/                   → ⚠️ TODOS los equipos — base común del backend
│   │   ├── dominio/
│   │   │   ├── modelos.py            → @dataclass Nodo, Arista, Red, ResultadoPropagacion
│   │   │   ├── enumeraciones.py      → TipoNodo, FaseSimulacion (espejo de tipos.ts)
│   │   │   ├── eventos.py            → RedActualizada, SimulacionIniciada, ErrorCalculo
│   │   │   ├── excepciones.py        → RedInvalidaError, ConvergenciaError, MatrizSingularError
│   │   │   └── validadores.py        → validar_red(), validar_arista(), validar_matriz()
│   │   ├── interfaces/
│   │   │   ├── i_motor_calculo.py    → Interface IMotorCalculo (SOLID I y D)
│   │   │   └── i_simulacion.py       → Interface ISimulacion (SOLID I y D)
│   │   └── utilidades.py             → generar_id(), formatear_resultado(), redondear()
│   │
│   ├── motor/                        → 🔴 SUBEQUIPO 2
│   │   ├── principal.py                    → FastAPI entrypoint (uvicorn motor.principal:app)
│   │   ├── network.json                    → ejemplo de red lógica
│   │   ├── dominio/
│   │   │   └── modelos.py                  → Variable, Connective, EPiCModel, PropagationState
│   │   ├── api/
│   │   │   ├── rutas.py                    → POST /api/v1/redes/{id}/calcular
│   │   │   └── esquemas.py                 → Pydantic: EntradaCalculo
│   │   ├── servicios/
│   │   │   ├── propagacion_servicio.py     → calcular_propagacion(), orquesta EPiCAdapter + EPiCEngine
│   │   │   └── construccion_matriz.py      → EPiCAdapter.network_to_model(), VisualizerAdapter.build_result()
│   │   ├── algoritmos/
│   │   │   ├── engine.py                   → EPiCEngine con worklist propagation (NEG, IMP, AND, OR)
│   │   │   ├── constantes.py               → Dominio 4-valor {N, T, F, B}
│   │   │   └── tablas.py                   → NEG_TABLE, IMP_TABLE, AND_TABLE, OR_TABLE
│   │   └── pruebas/
│   │       ├── test_engine.py              → Tests 8–13 (cadena, silogismo, De Morgan, dilemma, médico)
│   │       ├── test_propagacion_servicio.py→ Tests 1–7 (modus ponens, tollens, negación, etc.)
│   │       └── exportar_json.py            → Ejecuta tests y exporta resultados a JSON
│   │
│   ├── simulador/                    → 🔵 SUBEQUIPO 3
│   │   ├── servicios/
│   │   │   ├── simulacion_servicio.py    → iniciar_simulacion(), avanzar_paso(), pausar()
│   │   │   └── estado_simulacion.py      → Gestiona y persiste EstadoSimulacion
│   │   ├── api/
│   │   │   ├── rutas.py              → POST /api/v1/simulaciones, GET /api/v1/simulaciones/{id}
│   │   │   └── esquemas.py           → Pydantic: EntradaSimulacion, SalidaSimulacion
│   │   └── pruebas/
│   │       └── test_simulacion_servicio.py
│   │
│   ├── principal.py                  → App FastAPI: monta los routers de motor y simulador
│   ├── requerimientos.txt            → fastapi, uvicorn, numpy, pydantic, pytest
│   └── .env.ejemplo                  → DATABASE_URL, SECRET_KEY, TOLERANCIA
│
├── documentacion/                    → ⚠️ TODOS los equipos mantienen esto
│   ├── dominio-compartido.md         → Definición oficial de tipos y contratos JSON
│   ├── contrato-api.md               → Endpoints acordados con ejemplos de request/response
│   └── convenciones.md               → Reglas de nombres, git, commits
│
├── .github/
│   └── workflows/
│       └── ci.yml                    → Corre lint + pruebas automáticas en cada PR
├── .gitignore
└── README.md                         → Este archivo
```

---

## Estructura de datos compartida (contrato JSON)

Esta es la estructura que **todos los equipos deben respetar** al comunicarse.
El frontend la usa en `compartido/dominio/tipos.ts` y el backend en `compartido/dominio/modelos.py`.

### Nodo

```json
{
  "id": "nodo-001",
  "tipo": "AND",
  "etiqueta": "Nodo A",
  "propiedades": {
    "entradas": 2,
  },
  "posicion": {"x": 120, "y": 340}
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
  "metadatos": {
    "etiqueta": "Conexión A-B"
  }
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `string` | Formato: `"arista-{número}"` |
| `idOrigen` | `string` | ID del nodo de inicio |
| `idDestino` | `string` | ID del nodo de destino |
| `peso` | `número` | Peso de la conexión (usado en la matriz) |
| `metadatos` | `objeto` | Datos extra opcionales |

### Red

```json
{
  "id": "red-001",
  "nodos": [],
  "aristas": [],
  "version": 3
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `string` | Identificador de la red |
| `nodos` | `Nodo[]` | Lista de nodos |
| `aristas` | `Arista[]` | Lista de conexiones |
| `version` | `número entero` | Se incrementa con cada cambio; el visualizador lo usa para saber si redibujar |

### ResultadoPropagacion

```json
{
  "redId": "red-001",
  "iteraciones": 48,
  "valoresNodos": {
    "nodo-001": 1.0,
    "nodo-002": 0.83,
    "nodo-003": 0.61
  },
  "convergido": true,
  "error": null
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `redId` | `string` | ID de la red calculada |
| `iteraciones` | `número entero` | Cuántas iteraciones tomó |
| `valoresNodos` | `{ [idNodo]: número }` | Valor propagado por nodo |
| `convergido` | `booleano` | `true` si el algoritmo llegó a solución |
| `error` | `string \| null` | Mensaje si algo falló, `null` si todo bien |

### EstadoSimulacion

```json
{
  "fase": "corriendo",
  "pasoActual": 3,
  "historial": []
}
```

| Campo | Tipo | Opciones de `fase` |
|-------|------|---------------------|
| `fase` | `string` | `"inactivo"`, `"corriendo"`, `"pausado"`, `"completado"`, `"error"` |
| `pasoActual` | `número entero` | Índice del paso en curso |
| `historial` | `ResultadoPropagacion[]` | Todos los resultados anteriores |

---

## Contrato de API REST

Todos los endpoints usan prefijo `/api/v1/`. El body siempre es JSON.

| Método | Ruta | Quién llama | Quién responde | Descripción |
|--------|------|-------------|----------------|-------------|
| `POST` | `/api/v1/redes/{id}/calcular` | Simulador / Frontend | Motor | Dispara el cálculo matricial |
| `GET` | `/api/v1/propagaciones/{id}` | Visualizador | Motor | Obtiene un resultado guardado |
| `POST` | `/api/v1/simulaciones` | Frontend | Simulador | Inicia una simulación nueva |
| `GET` | `/api/v1/simulaciones/{id}` | Frontend | Simulador | Consulta el estado actual |
| `PUT` | `/api/v1/simulaciones/{id}/pausar` | Frontend | Simulador | Pausa la simulación |
| `PUT` | `/api/v1/simulaciones/{id}/avanzar` | Frontend | Simulador | Avanza un paso manual |

---

## Convenciones de nombres

### Frontend (TypeScript / React)

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| Componentes React | `PascalCase` | `CanvasEditor`, `GrafoVisual` |
| Hooks | `camelCase` con prefijo `use` | `useEditor`, `useSimulacion` |
| Variables y funciones | `camelCase` | `valorNodo`, `calcularPropagacion` |
| Interfaces y tipos | `PascalCase` | `Nodo`, `ResultadoPropagacion` |
| Constantes globales | `SCREAMING_SNAKE_CASE` | `MAX_ITERACIONES`, `API_BASE_URL` |
| Archivos componentes | `PascalCase.tsx` | `FormularioNodo.tsx` |
| Archivos hooks/utils | `camelCase.ts` | `useEditor.ts`, `utilidades.ts` |

### Backend (Python)

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| Variables y funciones | `snake_case` | `valor_nodo`, `calcular_propagacion` |
| Clases | `PascalCase` | `MotorPropagacion`, `ResultadoCalculo` |
| Constantes | `SCREAMING_SNAKE_CASE` | `MAX_ITERACIONES = 1000` |
| Atributos privados | `_snake_case` | `self._matriz_adyacencia` |
| Archivos | `snake_case.py` | `propagacion_servicio.py` |
| Interfaces (abstractas) | `I` + `PascalCase` | `IMotorCalculo`, `ISimulacion` |

### Prefijos de funciones acordados para todo el equipo

| Prefijo | Uso | Ejemplos |
|---------|-----|---------|
| `get` | Leer datos | `getNodo(id)`, `getResultado()` |
| `set` | Mutar estado local | `setEstado()`, `setFase()` |
| `calcular` | Operaciones matemáticas | `calcularPropagacion()`, `calcularMatriz()` |
| `simular` | Orquestar pasos | `simularPaso()`, `simularCompleto()` |
| `renderizar` | Dibujar en pantalla | `renderizarRed()`, `renderizarNodo()` |
| `validar` | Verificar integridad | `validarRed()`, `validarArista()` |
| `construir` | Crear estructuras | `construirMatriz()`, `construirGrafo()` |
| `use` | Hooks de React | `useEditor()`, `useSimulacion()` |

---

## Flujo de trabajo con Git

### Ramas principales

```
main          → código en producción, solo merge tras revisión total del equipo
develop       → integración continua, aquí llegan los PR de todas las ramas
```

### Nombrar tus ramas de trabajo

```
feature/editor-toolbar-nodos
feature/motor-algoritmo-gauss-seidel
feature/simulador-control-pasos
feature/visualizador-mapa-calor
fix/dominio-validacion-aristas
chore/setup-ci-pipeline
```

Formato: `tipo/componente-descripcion-corta`

Tipos válidos: `feature` (nueva función), `fix` (corrección), `chore` (configuración), `docs` (documentación).

### Proceso de entrega de cambios

1. Crear rama desde `develop`: `git checkout -b feature/mi-cambio develop`
2. Hacer commits pequeños y descriptivos en español
3. Abrir Pull Request hacia `develop`
4. Mínimo **1 persona de otro subequipo** debe aprobar el PR
5. Si el cambio toca `compartido/` → mínimo **1 persona de cada subequipo** debe aprobar

### Regla de commits

```
verbo en presente + qué hace + en qué módulo

agrega validación de aristas en validadores.ts
corrige cálculo de convergencia en gauss_seidel.py
mueve constantes a compartido/dominio/constantes.ts
```

---

## Plan de 10 semanas

| Semanas | Todos | Subequipo 1 — Editor | Subequipo 2 — Motor | Subequipo 3 — Simulador |
|---------|-------|----------------------|---------------------|--------------------------|
| 1–2 | Diseñar y acordar `compartido/dominio/` | Setup React + canvas base | Setup FastAPI + estructura motor | Definir API de simulación |
| 3–5 | Revisiones cruzadas de PRs | Editor funcional con datos mock | Algoritmos matriciales + pruebas | Lógica de pasos y estado |
| 6–8 | Integración progresiva | Conectar editor con API real | Optimización y pruebas de carga | Conectar simulador con motor |
| 9 | Construir `visualizador/` juntos | Componentes de visualización | Exportar datos para visualizador | Historial y replay de pasos |
| 10 | Pruebas de integración, ajustes y demo final | — | — | — |

---

## Cómo levantar el proyecto localmente

### Frontend

```bash
cd frontend
npm install
cp .env.ejemplo .env
npm run dev
```

Acceder en `http://localhost:5173`

### Backend

```bash
cd backend
python -m venv entorno
source entorno/bin/activate       # Windows: entorno\Scripts\activate
pip install -r requerimientos.txt
cp .env.ejemplo .env
uvicorn principal:app --reload
```

API disponible en `http://localhost:8000`
Documentación automática en `http://localhost:8000/docs`

---

## Principios SOLID aplicados

| Principio | Aplicación concreta en este proyecto |
|-----------|--------------------------------------|
| **S** — Responsabilidad única | `propagacion_servicio.py` solo orquesta; `gauss_seidel.py` solo calcula |
| **O** — Abierto/cerrado | Se puede agregar `newton_raphson.py` sin tocar `propagacion_servicio.py` |
| **L** — Sustitución de Liskov | `GaussSeidel` y `Jacobi` son intercambiables porque ambos implementan `IMotorCalculo` |
| **I** — Segregación de interfaces | `IMotorCalculo` solo expone lo que el motor necesita; `ISimulacion` solo lo del simulador |
| **D** — Inversión de dependencias | `SimulacionServicio` recibe un `IMotorCalculo`, no un `GaussSeidel` específico |
