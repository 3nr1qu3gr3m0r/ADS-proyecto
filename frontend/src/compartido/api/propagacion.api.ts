/**
 * propagacion.api.ts — API para cálculo de propagación
 */

import { API_BASE_URL } from '../dominio/constantes';
import type { Red } from '../dominio/tipos';

export async function calcularPropagacion(red: Red): Promise<{ id: string }> {
  const response = await fetch(`${API_BASE_URL}/calcular`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(red),
  });
  return response.json();
}

export async function obtenerResultado(id: string): Promise<unknown> {
  const response = await fetch(`${API_BASE_URL}/resultado/${id}`);
  return response.json();
}