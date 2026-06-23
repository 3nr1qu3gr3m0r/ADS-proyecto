/**
 * constantes.ts — Colores EPiC, presets y utilidades sin React.
 */

import type { ValorBelnap, Red } from './tipos';

// ── Paleta de colores por valor Belnap ───────────────────────────────────────

export const COLOR_BELNAP: Record<ValorBelnap, string> = {
  T: '#22c55e',   // verde  — verdadero
  F: '#ef4444',   // rojo   — falso
  B: '#f59e0b',   // naranja — ambos (contradicción)
  N: '#6b7280',   // gris   — sin evidencia
};

export const DESC_BELNAP: Record<ValorBelnap, string> = {
  T: 'Verdadero',
  F: 'Falso',
  B: 'Contradicción',
  N: 'Sin evidencia',
};

export const PALETA = {
  fondo:    '#071225',
  header:   '#08152f',
  tarjeta:  '#162849',
  elevado:  '#1e293b',
  borde:    '#1e3a5f',
  texto:    '#f1f5f9',
  acento:   '#6366f1',
} as const;

// ── Presets de ejemplo ───────────────────────────────────────────────────────

export const PRESETS: Record<string, Red> = {
  'modus-ponens': {
    id: 'red-mp', version: 1,
    nodos: [
      { id: 'nodo-P',  etiqueta: 'P',        tipo: 'premisa', propiedades: { valor: 'T' }, posicion: { x: 100, y: 200 } },
      { id: 'nodo-PQ', etiqueta: 'P → Q',    tipo: 'premisa', propiedades: { valor: 'T' }, posicion: { x: 100, y: 350 } },
      { id: 'nodo-A',  etiqueta: 'P ∧ (P→Q)',tipo: 'AND',     propiedades: {},             posicion: { x: 380, y: 275 } },
      { id: 'nodo-Q',  etiqueta: 'Q',         tipo: 'OR',      propiedades: {},             posicion: { x: 640, y: 275 } },
    ],
    aristas: [
      { id: 'arista-1', idOrigen: 'nodo-P',  idDestino: 'nodo-A',  peso: 1, metadatos: {} },
      { id: 'arista-2', idOrigen: 'nodo-PQ', idDestino: 'nodo-A',  peso: 1, metadatos: {} },
      { id: 'arista-3', idOrigen: 'nodo-A',  idDestino: 'nodo-Q',  peso: 1, metadatos: {} },
    ],
  },
  contradiccion: {
    id: 'red-contra', version: 1,
    nodos: [
      { id: 'nodo-P',   etiqueta: 'P',    tipo: 'premisa', propiedades: { valor: 'B' }, posicion: { x: 100, y: 275 } },
      { id: 'nodo-notP',etiqueta: '¬P',   tipo: 'NOT',     propiedades: {},             posicion: { x: 370, y: 150 } },
      { id: 'nodo-C',   etiqueta: 'P∧¬P', tipo: 'AND',     propiedades: {},             posicion: { x: 640, y: 275 } },
    ],
    aristas: [
      { id: 'arista-1', idOrigen: 'nodo-P',    idDestino: 'nodo-notP', peso: 1, metadatos: {} },
      { id: 'arista-2', idOrigen: 'nodo-P',    idDestino: 'nodo-C',    peso: 1, metadatos: {} },
      { id: 'arista-3', idOrigen: 'nodo-notP', idDestino: 'nodo-C',    peso: 1, metadatos: {} },
    ],
  },
  xor: {
    id: 'red-xor', version: 1,
    nodos: [
      { id: 'nodo-A', etiqueta: 'A (T)', tipo: 'premisa', propiedades: { valor: 'T' }, posicion: { x: 100, y: 180 } },
      { id: 'nodo-B', etiqueta: 'B (F)', tipo: 'premisa', propiedades: { valor: 'F' }, posicion: { x: 100, y: 380 } },
      { id: 'nodo-X', etiqueta: 'A ⊕ B', tipo: 'XOR',    propiedades: {},             posicion: { x: 440, y: 280 } },
    ],
    aristas: [
      { id: 'arista-1', idOrigen: 'nodo-A', idDestino: 'nodo-X', peso: 1, metadatos: {} },
      { id: 'arista-2', idOrigen: 'nodo-B', idDestino: 'nodo-X', peso: 1, metadatos: {} },
    ],
  },
};
