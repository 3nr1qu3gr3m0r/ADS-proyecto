/**
 * useSimulacion.ts — Hook que conecta con el simulador vía API
 */

import { useState, useCallback } from 'react';
import type { Red, ResultadoPropagacion } from '../dominio/tipos';
import { API_BASE_URL } from '../dominio/constantes';

export function useSimulacion() {
  const [cargando, setCargando] = useState(false);
  const [resultado, setResultado] = useState<ResultadoPropagacion | null>(null);

  const iniciarSimulacion = useCallback(async (red: Red) => {
    setCargando(true);
    try {
      const response = await fetch(`${API_BASE_URL}/simulaciones`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(red),
      });
      const data = await response.json();
      setResultado(data);
    } catch {
      setResultado({ exitosa: false, mensaje: 'Error de conexión', nodosProcesados: [], tiempoMs: 0 });
    } finally {
      setCargando(false);
    }
  }, []);

  return { cargando, resultado, iniciarSimulacion };
}