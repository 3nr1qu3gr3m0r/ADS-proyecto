/**
 * ============================================================
 * Prompt: "Implementa las interfaces compartidas del sistema:
 * Nodo, Arista, Conectivo, Matriz, Red, y tipos auxiliares
 * como ValorEvidencia, FormaNodo, ModoEditor, ModoCanvas.
 * Sigue SOLID ISP. Sin dependencias externas."
 * ============================================================
 * tipos.ts — Contratos Compartidos del Sistema (Shared Kernel)
 * ============================================================
 * SOLID:
 *  ISP: interfaces mínimas y cohesivas.
 *  SRP: cada interfaz modela una sola entidad.
 *  OCP: extensibles por composición, no por modificación.
 *  DIP: capas superiores dependen de estas abstracciones.
 *
 * Compatible con JSON. Sin dependencias externas.
 */

export type Id = string;

export interface Posicion {
  readonly x: number;
  readonly y: number;
}

// ─── Evidencia y Modos ──────────────────────────────────────

export type ValorEvidencia = 'T' | 'F' | 'B' | 'N';

export const COLOR_BORDE_EVIDENCIA: Record<ValorEvidencia, string> = {
  T: '#22c55e',
  F: '#ef4444',
  B: '#3b82f6',
  N: '#6b7280',
};

export type OperacionLogica = 'AND' | 'OR' | 'XOR' | 'NOR' | 'NAND' | 'NOT';

export type TipoNodo = 'evidencia' | 'operacion';

export type FormaNodo = 'circulo' | 'rectangulo' | 'rombo' | 'elipse';

export type EstiloLinea = 'solida' | 'discontinua' | 'punteada';

export type ModoEditor = 'EDIT' | 'EXECUTION';

export type ModoCanvas = 'select' | 'move' | 'conectar';

// ─── Nodo ───────────────────────────────────────────────────

export interface Nodo {
  readonly id: Id;
  readonly etiqueta: string;
  readonly tipo: TipoNodo;
  readonly operacion?: OperacionLogica;
  readonly valorInicial: ValorEvidencia;
  readonly valorActual: ValorEvidencia;
  readonly peso: number;
  readonly posicion: Posicion;
  readonly color: string;
  readonly tamano: number;
  readonly forma: FormaNodo;
  readonly visible: boolean;
  readonly metadatos: Readonly<Record<string, string>>;
}

// ─── Arista ─────────────────────────────────────────────────

export interface Arista {
  readonly id: Id;
  readonly origenId: Id;
  readonly destinoId: Id;
  readonly peso: number;
  readonly color: string;
  readonly grosor: number;
  readonly estilo: EstiloLinea;
  readonly metadatos: Readonly<Record<string, string>>;
}

// ─── Conectivo ──────────────────────────────────────────────

export interface Conectivo {
  readonly id: Id;
  readonly inputVariableIds: readonly Id[];
  readonly outputVariableIds: readonly Id[];
  readonly matrizId: Id;
}

// ─── Matriz ─────────────────────────────────────────────────

export interface Matriz {
  readonly id: Id;
  readonly conectivoId: Id;
  readonly rows: number;
  readonly cols: number;
  readonly valores: readonly (readonly number[])[];
}

// ─── Red ────────────────────────────────────────────────────

export interface Red {
  readonly id: Id;
  readonly nombre: string;
  readonly nodos: readonly Nodo[];
  readonly aristas: readonly Arista[];
  readonly conectivos: readonly Conectivo[];
  readonly matrices: readonly Matriz[];
  readonly modo: ModoEditor;
}

// ─── Resultado ──────────────────────────────────────────────

export interface ResultadoPropagacion {
  readonly exitosa: boolean;
  readonly mensaje: string;
  readonly nodosProcesados: readonly string[];
  readonly tiempoMs: number;
}

// ─── Error ──────────────────────────────────────────────────

export interface ErrorValidacion {
  readonly codigo: string;
  readonly mensaje: string;
  readonly nodoId?: Id;
  readonly aristaId?: Id;
  readonly conectivoId?: Id;
  readonly matrizId?: Id;
}