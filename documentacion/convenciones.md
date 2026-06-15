# Convenciones del proyecto

## Nombrado

### Frontend (TypeScript / React)

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| Componentes React | `PascalCase` | `CanvasEditor` |
| Hooks | `camelCase` con prefijo `use` | `useEditor` |
| Variables y funciones | `camelCase` | `valorNodo` |
| Interfaces y tipos | `PascalCase` | `Nodo` |
| Constantes globales | `SCREAMING_SNAKE_CASE` | `MAX_ITERACIONES` |
| Archivos componentes | `PascalCase.tsx` | `FormularioNodo.tsx` |
| Archivos hooks/utils | `camelCase.ts` | `useEditor.ts` |

### Backend (Python)

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| Variables y funciones | `snake_case` | `valor_nodo` |
| Clases | `PascalCase` | `MotorPropagacion` |
| Constantes | `SCREAMING_SNAKE_CASE` | `MAX_ITERACIONES = 1000` |
| Atributos privados | `_snake_case` | `self._matriz_adyacencia` |
| Archivos | `snake_case.py` | `propagacion_servicio.py` |
| Interfaces (abstractas) | `I` + `PascalCase` | `IMotorCalculo` |

## Prefijos de funciones

| Prefijo | Uso | Ejemplos |
|---------|-----|----------|
| `get` | Leer datos | `getNodo(id)`, `getResultado()` |
| `set` | Mutar estado local | `setEstado()`, `setFase()` |
| `calcular` | Operaciones matemáticas | `calcularPropagacion()`, `calcularMatriz()` |
| `simular` | Orquestar pasos | `simularPaso()`, `simularCompleto()` |
| `validar` | Verificar integridad | `validarRed()`, `validarArista()` |
| `construir` | Crear estructuras | `construirMatriz()`, `construirGrafo()` |
| `use` | Hooks de React | `useEditor()`, `useSimulacion()` |

## Git

### Ramas

```
main          → producción (solo merge tras revisión total)
develop       → integración continua (PRs hacia aquí)
```

Nomenclatura: `tipo/componente-descripcion-corta`
Tipos: `feature`, `fix`, `chore`, `docs`

### Commits

```
verbo en presente + qué hace + en qué módulo

agrega validación de aristas en validores.ts
corrige cálculo de convergencia en gauss_seidel.py
mueve constantes a compartido/dominio/constantes.ts
```

### Reglas de revisión

- PRs hacia `develop`: mínimo 1 persona de otro subequipo aprueba
- Cambios en `compartido/`: mínimo 1 persona de **cada** subequipo aprueba