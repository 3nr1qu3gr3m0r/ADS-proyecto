import type {
  Nodo, Arista, Red, Conectivo, Matriz,
  ErrorValidacion, Id, ValorEvidencia, OperacionLogica,
} from './tipos';

/**
 * ============================================================
 * Prompt: "Crea funciones de validación puras para Nodo,
 * Arista, Red (con detección de ciclos DFS), Conectivo y
 * Matriz. Reutilizable frontend/backend."
 * ============================================================
 * validadores.ts — Validación Pura del Grafo
 * ============================================================
 * Funciones sin efectos secundarios. Reutilizables frontend/backend.
 */

// ─── Helpers ────────────────────────────────────────────────

type ColorVisita = 'blanco' | 'gris' | 'negro';

const VALORES_EVIDENCIA: readonly ValorEvidencia[] = ['T', 'F', 'B', 'N'];
const OPERACIONES_LOGICAS: readonly OperacionLogica[] = ['AND', 'OR', 'XOR', 'NOR', 'NAND', 'NOT'];

function detectarCiclos(nodos: readonly Nodo[], aristas: readonly Arista[]): boolean {
  const ady = new Map<Id, Id[]>();
  for (const n of nodos) ady.set(n.id, []);
  for (const a of aristas) ady.get(a.origenId)?.push(a.destinoId);

  const color = new Map<Id, ColorVisita>();
  for (const n of nodos) color.set(n.id, 'blanco');

  function dfs(id: Id): boolean {
    color.set(id, 'gris');
    for (const v of ady.get(id) ?? []) {
      const c = color.get(v);
      if (c === 'gris') return true;
      if (c === 'blanco' && dfs(v)) return true;
    }
    color.set(id, 'negro');
    return false;
  }

  for (const n of nodos) {
    if (color.get(n.id) === 'blanco' && dfs(n.id)) return true;
  }
  return false;
}

// ─── Valor evidencial ───────────────────────────────────────

export function validarValorEvidencia(valor: string, campo: string, id?: Id): ErrorValidacion[] {
  const errores: ErrorValidacion[] = [];
  if (!VALORES_EVIDENCIA.includes(valor as ValorEvidencia)) {
    errores.push({
      codigo: 'VALOR_EVIDENCIA_INVALIDO',
      mensaje: `"${campo}" debe ser uno de: ${VALORES_EVIDENCIA.join(', ')}. Recibido: "${valor}".`,
      nodoId: id,
    });
  }
  return errores;
}

// ─── validarNodo ────────────────────────────────────────────

export function validarNodo(
  nodo: Nodo,
  idsExistentes?: Set<Id>,
): ErrorValidacion[] {
  const errores: ErrorValidacion[] = [];

  if (!nodo.id) errores.push({ codigo: 'NODO_SIN_ID', mensaje: 'El nodo no tiene identificador.' });
  if (!nodo.etiqueta?.trim()) errores.push({ codigo: 'NODO_SIN_NOMBRE', mensaje: `El nodo "${nodo.id}" no tiene etiqueta.`, nodoId: nodo.id });
  if (typeof nodo.peso !== 'number' || !Number.isFinite(nodo.peso)) errores.push({ codigo: 'PESO_INVALIDO', mensaje: `Nodo "${nodo.id}" peso inválido: ${nodo.peso}.`, nodoId: nodo.id });
  if (!Number.isFinite(nodo.posicion?.x) || !Number.isFinite(nodo.posicion?.y)) errores.push({ codigo: 'POSICION_INVALIDA', mensaje: `Nodo "${nodo.id}" coordenadas inválidas.`, nodoId: nodo.id });
  if (idsExistentes?.has(nodo.id)) errores.push({ codigo: 'NODO_DUPLICADO', mensaje: `Ya existe nodo con id "${nodo.id}".`, nodoId: nodo.id });

  if (nodo.tipo === 'operacion') {
    if (!nodo.operacion) {
      errores.push({ codigo: 'OPERACION_FALTANTE', mensaje: `Nodo "${nodo.id}" es de tipo operación pero no tiene operación asignada.`, nodoId: nodo.id });
    } else if (!OPERACIONES_LOGICAS.includes(nodo.operacion)) {
      errores.push({ codigo: 'OPERACION_INVALIDA', mensaje: `Nodo "${nodo.id}" operación inválida: "${nodo.operacion}".`, nodoId: nodo.id });
    }
  } else if (nodo.tipo === 'evidencia') {
    errores.push(...validarValorEvidencia(nodo.valorInicial, 'valorInicial', nodo.id));
    errores.push(...validarValorEvidencia(nodo.valorActual, 'valorActual', nodo.id));
  }

  if (typeof nodo.tamano !== 'number' || nodo.tamano <= 0) {
    errores.push({ codigo: 'TAMANO_INVALIDO', mensaje: `Nodo "${nodo.id}" tamaño inválido: ${nodo.tamano}.`, nodoId: nodo.id });
  }

  if (typeof nodo.color !== 'string' || !nodo.color.startsWith('#')) {
    errores.push({ codigo: 'COLOR_INVALIDO', mensaje: `Nodo "${nodo.id}" color inválido: "${nodo.color}". Debe ser hex.`, nodoId: nodo.id });
  }

  return errores;
}

// ─── validarArista ──────────────────────────────────────────

export function validarArista(
  arista: Arista,
  idsNodos: Set<Id>,
  idsAristas?: Set<Id>,
  nodos?: readonly Nodo[],
): ErrorValidacion[] {
  const errores: ErrorValidacion[] = [];

  if (!arista.id) errores.push({ codigo: 'ARISTA_SIN_ID', mensaje: 'La arista no tiene identificador.' });
  if (!idsNodos.has(arista.origenId)) errores.push({ codigo: 'REFERENCIA_ORIGEN_INEXISTENTE', mensaje: `Arista "${arista.id}" referencia origen "${arista.origenId}" inexistente.`, aristaId: arista.id });
  if (!idsNodos.has(arista.destinoId)) errores.push({ codigo: 'REFERENCIA_DESTINO_INEXISTENTE', mensaje: `Arista "${arista.id}" referencia destino "${arista.destinoId}" inexistente.`, aristaId: arista.id });
  if (typeof arista.peso !== 'number' || !Number.isFinite(arista.peso)) errores.push({ codigo: 'PESO_ARISTA_INVALIDO', mensaje: `Arista "${arista.id}" peso inválido: ${arista.peso}.`, aristaId: arista.id });
  if (idsAristas?.has(arista.id)) errores.push({ codigo: 'ARISTA_DUPLICADA', mensaje: `Ya existe arista con id "${arista.id}".`, aristaId: arista.id });
  if (typeof arista.grosor !== 'number' || arista.grosor <= 0) errores.push({ codigo: 'GROSOR_INVALIDO', mensaje: `Arista "${arista.id}" grosor inválido.`, aristaId: arista.id });
  if (!arista.color?.startsWith('#')) errores.push({ codigo: 'COLOR_ARISTA_INVALIDO', mensaje: `Arista "${arista.id}" color inválido.`, aristaId: arista.id });

  if (nodos) {
    const origen = nodos.find((n) => n.id === arista.origenId);
    const destino = nodos.find((n) => n.id === arista.destinoId);
    if (origen && destino && origen.tipo === 'evidencia' && destino.tipo === 'evidencia') {
      errores.push({ codigo: 'CONEXION_INVALIDA', mensaje: `No se puede conectar dos nodos de evidencia directamente.`, aristaId: arista.id });
    }
  }

  return errores;
}

// ─── validarConectivo ──────────────────────────────────────

export function validarConectivo(
  conectivo: Conectivo,
  idsNodos: Set<Id>,
  idsConectivos?: Set<Id>,
): ErrorValidacion[] {
  const errores: ErrorValidacion[] = [];

  if (!conectivo.id) errores.push({ codigo: 'CONECTIVO_SIN_ID', mensaje: 'Conectivo sin identificador.' });
  if (idsConectivos?.has(conectivo.id)) errores.push({ codigo: 'CONECTIVO_DUPLICADO', mensaje: `Conectivo "${conectivo.id}" duplicado.`, conectivoId: conectivo.id });

  if (!conectivo.inputVariableIds || conectivo.inputVariableIds.length === 0) {
    errores.push({ codigo: 'CONECTIVO_SIN_INPUTS', mensaje: `Conectivo "${conectivo.id}" sin variables de entrada.`, conectivoId: conectivo.id });
  }
  if (!conectivo.outputVariableIds || conectivo.outputVariableIds.length === 0) {
    errores.push({ codigo: 'CONECTIVO_SIN_OUTPUTS', mensaje: `Conectivo "${conectivo.id}" sin variables de salida.`, conectivoId: conectivo.id });
  }

  for (const vid of [...conectivo.inputVariableIds, ...conectivo.outputVariableIds]) {
    if (!idsNodos.has(vid)) {
      errores.push({ codigo: 'CONECTIVO_VAR_INEXISTENTE', mensaje: `Conectivo "${conectivo.id}" referencia variable "${vid}" inexistente.`, conectivoId: conectivo.id });
    }
  }

  return errores;
}

// ─── validarMatriz ─────────────────────────────────────────

export function validarMatriz(
  matriz: Matriz,
  idsConectivos: Set<Id>,
  idsMatrices?: Set<Id>,
): ErrorValidacion[] {
  const errores: ErrorValidacion[] = [];

  if (!matriz.id) errores.push({ codigo: 'MATRIZ_SIN_ID', mensaje: 'Matriz sin identificador.' });
  if (idsMatrices?.has(matriz.id)) errores.push({ codigo: 'MATRIZ_DUPLICADA', mensaje: `Matriz "${matriz.id}" duplicada.`, matrizId: matriz.id });
  if (!idsConectivos.has(matriz.conectivoId)) errores.push({ codigo: 'MATRIZ_CONECTIVO_INEXISTENTE', mensaje: `Matriz "${matriz.id}" referencia conectivo "${matriz.conectivoId}" inexistente.`, matrizId: matriz.id });

  if (!matriz.valores || matriz.valores.length === 0) {
    errores.push({ codigo: 'MATRIZ_VACIA', mensaje: `Matriz "${matriz.id}" sin valores.`, matrizId: matriz.id });
  } else {
    const cols = matriz.valores[0]!.length;
    for (let i = 0; i < matriz.valores.length; i++) {
      if (matriz.valores[i]!.length !== cols) {
        errores.push({ codigo: 'MATRIZ_FILA_HETEROGENEA', mensaje: `Matriz "${matriz.id}" fila ${i} tiene ${matriz.valores[i]!.length} columnas, se esperaban ${cols}.`, matrizId: matriz.id });
      }
      for (let j = 0; j < matriz.valores[i]!.length; j++) {
        if (typeof matriz.valores[i]![j] !== 'number' || !Number.isFinite(matriz.valores[i]![j])) {
          errores.push({ codigo: 'MATRIZ_VALOR_INVALIDO', mensaje: `Matriz "${matriz.id}" [${i}][${j}] valor inválido.`, matrizId: matriz.id });
        }
      }
    }
  }

  return errores;
}

// ─── validarRed ─────────────────────────────────────────────

export function validarRed(red: Red): ErrorValidacion[] {
  const errores: ErrorValidacion[] = [];

  if (!red.id) errores.push({ codigo: 'RED_SIN_ID', mensaje: 'La red no tiene identificador.' });
  if (!red.nombre?.trim()) errores.push({ codigo: 'RED_SIN_NOMBRE', mensaje: 'La red no tiene nombre.' });

  if (!red.nodos || red.nodos.length === 0) {
    errores.push({ codigo: 'GRAFO_VACIO', mensaje: 'La red no contiene nodos.' });
    return errores;
  }

  const idsNodos = new Set<Id>();
  const idsAristas = new Set<Id>();
  const idsConectivos = new Set<Id>();
  const idsMatrices = new Set<Id>();

  for (const n of red.nodos) { errores.push(...validarNodo(n, idsNodos)); idsNodos.add(n.id); }
  for (const a of red.aristas) { errores.push(...validarArista(a, idsNodos, idsAristas, red.nodos)); idsAristas.add(a.id); }
  for (const c of red.conectivos) { errores.push(...validarConectivo(c, idsNodos, idsConectivos)); idsConectivos.add(c.id); }
  for (const m of red.matrices) { errores.push(...validarMatriz(m, idsConectivos, idsMatrices)); idsMatrices.add(m.id); }

  if (red.aristas.length > 0 && detectarCiclos(red.nodos, red.aristas)) {
    errores.push({ codigo: 'CICLO_DETECTADO', mensaje: 'La red contiene uno o más ciclos dirigidos.' });
  }

  return errores;
}