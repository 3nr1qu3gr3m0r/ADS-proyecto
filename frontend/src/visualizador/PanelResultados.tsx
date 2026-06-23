/**
 * PanelResultados.tsx — Valores T/F/B/N por nodo + leyenda Belnap.
 */

import type { NodoConValor } from '../compartido/tipos';
import { COLOR_BELNAP, DESC_BELNAP } from '../compartido/constantes';

interface Props {
  nodos: NodoConValor[];
  iteraciones: number;
  convergido: boolean;
}

export function PanelResultados({ nodos, iteraciones, convergido }: Props) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>

      {/* Métricas */}
      <div style={cardSt}>
        <h3 style={h3St}>Propagación</h3>
        <Row label="Algoritmo"   value="Tablas EPiC (Belnap)" />
        <Row label="Iteraciones" value={String(iteraciones)} />
        <Row label="Convergencia"
          value={convergido ? '✓ Punto fijo alcanzado' : '⏳ En progreso'}
          color={convergido ? '#22c55e' : '#f59e0b'} />
      </div>

      {/* Valores por nodo */}
      {nodos.length > 0 && (
        <div style={cardSt}>
          <h3 style={h3St}>Valores de nodos</h3>
          {nodos.map(n => {
            const color = COLOR_BELNAP[n.valorActual];
            return (
              <div key={n.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
                <div>
                  <div style={{ fontSize: 12, color: 'white', fontWeight: 600 }}>
                    {n.tipo === 'premisa' && <span style={{ color: '#f59e0b' }}>★ </span>}
                    {n.etiqueta}
                  </div>
                  <div style={{ fontSize: 10, color: '#64748b' }}>{n.id} · {n.tipo}</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <div style={{ width: 28, height: 28, borderRadius: '50%', background: color,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontWeight: 'bold', fontSize: 14, color: 'white' }}>
                    {n.valorActual}
                  </div>
                  <span style={{ fontSize: 11, color: '#94a3b8' }}>{DESC_BELNAP[n.valorActual]}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Leyenda Belnap */}
      <div style={cardSt}>
        <h3 style={h3St}>Leyenda Belnap</h3>
        {(['T','F','B','N'] as const).map(v => (
          <div key={v} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
            <div style={{ width: 28, height: 28, borderRadius: '50%', background: COLOR_BELNAP[v],
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontWeight: 'bold', fontSize: 14, color: 'white', flexShrink: 0 }}>
              {v}
            </div>
            <div>
              <div style={{ fontSize: 12, color: 'white', fontWeight: 600 }}>{DESC_BELNAP[v]}</div>
              <div style={{ fontSize: 10, color: '#64748b' }}>
                { v === 'T' ? 'Solo evidencia positiva'
                : v === 'F' ? 'Solo evidencia negativa'
                : v === 'B' ? 'Evidencia positiva Y negativa (contradicción)'
                :              'Sin evidencia (indeterminado)' }
              </div>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}

function Row({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6, fontSize: 12 }}>
      <span style={{ color: '#94a3b8' }}>{label}</span>
      <span style={{ color: color ?? 'white', fontWeight: 600 }}>{value}</span>
    </div>
  );
}

const cardSt: React.CSSProperties = { background: '#162849', borderRadius: 14, padding: '14px 16px' };
const h3St:   React.CSSProperties = { fontSize: 11, color: '#94a3b8', fontWeight: 700,
  textTransform: 'uppercase', letterSpacing: 1, marginBottom: 10 };
