/**
 * eventos.ts — Tipos de eventos del sistema
 */

export interface RedActualizada {
  tipo: 'RedActualizada';
  redId: string;
}

export interface SimulacionIniciada {
  tipo: 'SimulacionIniciada';
  redId: string;
}

export interface ErrorCalculo {
  tipo: 'ErrorCalculo';
  mensaje: string;
}

export type EventoSistema = RedActualizada | SimulacionIniciada | ErrorCalculo;