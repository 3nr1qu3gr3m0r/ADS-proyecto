/**
 * useRed.ts — Hook de estado global de la red
 */

import { useState, useCallback } from 'react';
import type { Red } from '../dominio/tipos';

const RED_VACIA: Red = {
  id: 'red-1',
  nombre: 'Mi Red',
  nodos: [],
  aristas: [],
  conectivos: [],
  matrices: [],
  modo: 'EDIT',
};

export function useRed() {
  const [red, setRed] = useState<Red>(RED_VACIA);

  const actualizarRed = useCallback((nuevaRed: Red) => {
    setRed(nuevaRed);
  }, []);

  return { red, actualizarRed };
}