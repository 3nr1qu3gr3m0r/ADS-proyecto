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
  /**
   * Ejemplo de la Figura 2 del paper EPiC (página 17).
   * Premisas: (1) ∀x(B(x)→A(x))  (2) ∃x(¬C(x)∧¬A(x))
   * Conclusión: ∃x(¬C(x)∧¬B(x))
   *
   * Mapeo de pasos al grafo:
   *   (3) ★ ¬C(a)∧¬A(a) = T      premisa (instancia de ∃E)
   *   (4) ¬C(a) = T              OR passthrough ← (3)   [∧E]
   *   (5) ¬A(a) = T              OR passthrough ← (3)   [∧E]
   *   (6) A(a)  = F              NOT ← (5)              [¬E]  — nodo visual
   *   ★ B(a)→A(a) = T            premisa (instancia de ∀E)
   *   MT: recibe [B(a)→A(a)=T, ¬A(a)=T] → ¬B(a) = T   [MT + ¬I combinados]
   *   (9) ¬C(a)∧¬B(a) = T       AND ← (4) y ¬B(a)     [∧I]
   *
   * Nota sobre MT en EPiC Playground:
   *   MT(implicacion, consecuente_negado) → antecedente_negado
   *   1ª arista = B(a)→A(a)  [la implicación]
   *   2ª arista = ¬A(a)      [el consecuente negado — ¬ del consecuente de la implicación]
   *   Resultado = ¬B(a)      [el antecedente negado, que es lo que el paper llama paso 8]
   */
  'epic-fig2': {
    id: 'red-epic-fig2', version: 1,
    /**
     * Figura 2b del paper EPiC (pag. 17).
     * MT(implicacion, consecuente) → antecedente   [paso 7: B(a)=F]
     * NOT(antecedente)             → neg-antecedente [paso 8: ¬B(a)=T]
     */
    nodos: [
      // (3) ★ Premisa: ¬C(a)∧¬A(a) = T  [∃E de Assumption 2]
      { id: 'nodo-001', etiqueta: '¬C(a) ∧ ¬A(a)', tipo: 'premisa',
        propiedades: { valor: 'T' }, posicion: { x: 110, y: 200 } },

      // ★ Premisa: B(a)→A(a) = T  [∀E de Assumption 1]
      { id: 'nodo-005', etiqueta: 'B(a)→A(a)', tipo: 'premisa',
        propiedades: { valor: 'T' }, posicion: { x: 110, y: 420 } },

      // (4) ¬C(a) = T  [∧E de (3)]
      { id: 'nodo-002', etiqueta: '¬C(a)', tipo: 'OR', propiedades: {}, posicion: { x: 350, y: 110 } },

      // (5) ¬A(a) = T  [∧E de (3)]
      { id: 'nodo-003', etiqueta: '¬A(a)', tipo: 'OR', propiedades: {}, posicion: { x: 240, y: 320 } },

      // (6) A(a) = F   [¬E de (5)]
      { id: 'nodo-004', etiqueta: 'A(a)', tipo: 'NOT', propiedades: {}, posicion: { x: 420, y: 420 } },

      // (7) B(a) = F   [MT de Assumption 1 y (6)]
      //     MT: 1ª entrada = implicacion B(a)→A(a), 2ª = consecuente A(a)
      { id: 'nodo-006', etiqueta: 'B(a)', tipo: 'MT', propiedades: {}, posicion: { x: 590, y: 420 } },

      // (8) ¬B(a) = T  [¬I de (7)]
      { id: 'nodo-008', etiqueta: '¬B(a)', tipo: 'NOT', propiedades: {}, posicion: { x: 700, y: 310 } },

      // (9) ¬C(a)∧¬B(a) = T  [∧I de (4) y (8)]
      { id: 'nodo-007', etiqueta: '¬C(a) ∧ ¬B(a)', tipo: 'AND', propiedades: {}, posicion: { x: 760, y: 170 } },
    ],
    aristas: [
      // ∧E: premisa conjuntiva → ¬C(a)
      { id: 'arista-001', idOrigen: 'nodo-001', idDestino: 'nodo-002', peso: 1, metadatos: {} },
      // ∧E: premisa conjuntiva → ¬A(a)
      { id: 'arista-002', idOrigen: 'nodo-001', idDestino: 'nodo-003', peso: 1, metadatos: {} },
      // ¬E: ¬A(a) → NOT → A(a)
      { id: 'arista-003', idOrigen: 'nodo-003', idDestino: 'nodo-004', peso: 1, metadatos: {} },
      // MT: 1ª = implicacion B(a)→A(a)
      { id: 'arista-004', idOrigen: 'nodo-005', idDestino: 'nodo-006', peso: 1, metadatos: {} },
      // MT: 2ª = consecuente A(a)
      { id: 'arista-005', idOrigen: 'nodo-004', idDestino: 'nodo-006', peso: 1, metadatos: {} },
      // ¬I: B(a) → NOT → ¬B(a)
      { id: 'arista-006', idOrigen: 'nodo-006', idDestino: 'nodo-008', peso: 1, metadatos: {} },
      // ∧I: ¬C(a) → AND
      { id: 'arista-007', idOrigen: 'nodo-002', idDestino: 'nodo-007', peso: 1, metadatos: {} },
      // ∧I: ¬B(a) → AND
      { id: 'arista-008', idOrigen: 'nodo-008', idDestino: 'nodo-007', peso: 1, metadatos: {} },
    ],
  },
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
