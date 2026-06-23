// ============ PROMPT ============
// Implementa los controles de simulación React: botón Simular que dispara la
// propagación, barra de progreso de iteraciones actual/total, botones play/pausa/
// avanzar/retroceder/reiniciar con indicador visual de punto fijo alcanzado o error.
// ======== FIN DEL PROMPT ========

/**
 * ControlesSimulacion.tsx — Controles de navegación de la simulación.
 * Sin selector de algoritmo (solo hay un algoritmo: tablas EPiC).
 */

import type { FaseSimulacion } from '../compartido/tipos';

interface Props {
  fase: FaseSimulacion;
  pasoActual: number;
  totalPasos: number;
  cargando: boolean;
  onSimular: () => void;
  onPlay: () => void;
  onPausar: () => void;
  onPaso: () => void;
  onRetroceder: () => void;
  onReiniciar: () => void;
}

export function ControlesSimulacion({
  fase, pasoActual, totalPasos, cargando,
  onSimular, onPlay, onPausar, onPaso, onRetroceder, onReiniciar,
}: Props) {
  const enSim = fase !== 'inactivo';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>

      <div style={{ background: '#0f1f3d', borderRadius: 8, padding: '6px 10px', fontSize: 11, color: '#64748b' }}>
        Motor: <strong style={{ color: '#818cf8' }}>Tablas de verdad EPiC (Belnap 4 valores)</strong>
      </div>

      {!enSim ? (
        <button onClick={onSimular} disabled={cargando} style={btnPriSt}>
          {cargando ? '⏳ Calculando...' : '▶ Simular red'}
        </button>
      ) : (
        <>
          {/* Progreso */}
          <div style={{ background: '#0f1f3d', borderRadius: 8, padding: '8px 12px', fontSize: 12, color: '#94a3b8' }}>
            Iteración{' '}
            <span style={{ color: 'white', fontWeight: 'bold' }}>{pasoActual + 1}</span>
            {' / '}
            <span style={{ color: 'white', fontWeight: 'bold' }}>{totalPasos}</span>
            {fase === 'completado' && <span style={{ color: '#22c55e', marginLeft: 8 }}>✓ Punto fijo</span>}
            {fase === 'error'      && <span style={{ color: '#ef4444', marginLeft: 8 }}>✗ Error</span>}
          </div>

          <div style={{ display: 'flex', gap: 6 }}>
            <button onClick={onRetroceder} disabled={pasoActual === 0}          style={btnSecSt} title="Iteración anterior">⏮</button>
            {fase === 'corriendo'
              ? <button onClick={onPausar}  style={{ ...btnSecSt, flex: 1 }}>⏸ Pausar</button>
              : <button onClick={onPlay}    style={{ ...btnSecSt, flex: 1 }}>▶ Auto</button>
            }
            <button onClick={onPaso}    disabled={pasoActual >= totalPasos - 1} style={btnSecSt} title="Siguiente iteración">⏭</button>
          </div>

          <button onClick={onReiniciar} style={{ ...btnSecSt, color: '#f87171' }}>
            🔄 Nueva simulación
          </button>
        </>
      )}
    </div>
  );
}

const btnPriSt: React.CSSProperties = {
  background: '#6366f1', border: 'none', color: 'white', borderRadius: 8,
  padding: '10px 0', fontSize: 13, fontWeight: 'bold', cursor: 'pointer',
};
const btnSecSt: React.CSSProperties = {
  background: '#162849', border: '1px solid #1e3a5f', color: 'white',
  borderRadius: 8, padding: '8px 14px', fontSize: 13, cursor: 'pointer',
};
