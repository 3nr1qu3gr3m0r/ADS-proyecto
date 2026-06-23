// ============ PROMPT ============
// Define los tipos TypeScript del dominio EPiC: ValorBelnap (T/F/B/N),
// OperadorLogico (AND/OR/XOR/NOT/IMP), interfaces Nodo, Arista, Red,
// ResultadoPropagacion, EstadoSimulacion y NodoConValor enriquecido
// con el valor Belnap actual para renderizado coloreado en el canvas.
// ======== FIN DEL PROMPT ========

/**
 * tipos.ts — Contratos de datos EPiC.
 *
 * Dominio: lógica evidencial de 4 valores (Belnap)
 *   T = Verdadero  (evidencia positiva)
 *   F = Falso      (evidencia negativa)
 *   B = Ambos      (contradicción)
 *   N = Ninguno    (sin evidencia)
 *
 * Nodo premisa  → tiene valor fijo T/F/B/N asignado por el usuario.
 *                 Solo puede tener aristas SALIENTES (nunca entrantes).
 * Nodo operador → AND | OR | XOR | NOT — valor calculado por las tablas.
 */

export type Id = string;

export interface Posicion {
  x: number;
  y: number;
}

export type ValorBelnap = 'T' | 'F' | 'B' | 'N';
export type OperadorLogico = 'AND' | 'OR' | 'XOR' | 'NOT' | 'IMP';
export type TipoNodo = 'premisa' | OperadorLogico;

export interface PropiedadesNodo {
  valor?: ValorBelnap;   // solo para nodos premisa
}

export interface Nodo {
  id: Id;
  etiqueta: string;
  tipo: TipoNodo;
  propiedades: PropiedadesNodo;
  posicion: Posicion;
}

export interface Arista {
  id: Id;
  idOrigen: Id;
  idDestino: Id;
  peso: number;
  metadatos: Record<string, string>;
}

export interface Red {
  id: Id;
  nodos: Nodo[];
  aristas: Arista[];
  version: number;
}

export interface ResultadoPropagacion {
  redId: string;
  iteraciones: number;
  valoresNodos: Record<Id, ValorBelnap>;
  convergido: boolean;
  error: string | null;
}

export type FaseSimulacion = 'inactivo' | 'corriendo' | 'pausado' | 'completado' | 'error';

export interface EstadoSimulacion {
  id: string;
  fase: FaseSimulacion;
  pasoActual: number;
  historial: ResultadoPropagacion[];
}

/** Nodo enriquecido con el valor del paso visible actualmente */
export interface NodoConValor extends Nodo {
  valorActual: ValorBelnap;
}
