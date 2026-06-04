/**
 * utilidades.ts — Funciones de utilidad compartidas
 */

export function formatearValor(valor: number): string {
  return valor.toFixed(4);
}

export function generarId(prefix: string = 'id'): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function redondear(valor: number, decimales: number = 4): number {
  return Math.round(valor * 10 ** decimales) / 10 ** decimales;
}