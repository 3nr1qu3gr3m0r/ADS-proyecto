/**
 * simulacion.api.ts — API para simulaciones
 */

import { API_BASE_URL } from '../dominio/constantes';
import type { Red } from '../dominio/tipos';

export async function crearSimulacion(red: Red): Promise<{ id: string }> {
  const response = await fetch(`${API_BASE_URL}/simulaciones`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(red),
  });
  return response.json();
}

export async function obtenerSimulacion(id: string): Promise<unknown> {
  const response = await fetch(`${API_BASE_URL}/simulaciones/${id}`);
  return response.json();
}