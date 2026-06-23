// ============ PROMPT ============
// Implementa un canvas SVG interactivo con React que renderiza los nodos
// (círculos para operadores, rombos para premisas) y aristas (líneas con punta
// de flecha) de una red EPiC, soporta drag-and-drop de nodos con refs para evitar
// stale-closure, colorea por valor Belnap en modo simulación y elimina con doble/simple clic.
// ======== FIN DEL PROMPT ========

/**
 * CanvasEditor.tsx — Canvas SVG: editor + visualizador integrados.
 * Colores por valor T/F/B/N. Flechas animadas en modo simulación.
 * Drag-and-drop estable con refs (evita stale-closure).
 */

import { useRef, useEffect, useCallback } from 'react';
import type { Nodo, Arista, NodoConValor, ValorBelnap } from '../compartido/tipos';
import { COLOR_BELNAP, DESC_BELNAP, PALETA } from '../compartido/constantes';

const R = 38;

const ETIQ_BELNAP: Record<ValorBelnap, string> = { T: 'T', F: 'F', B: 'B', N: 'N' };

interface Props {
  nodos: Nodo[];
  aristas: Arista[];
  nodosConValor?: NodoConValor[];
  onMoverNodo: (id: string, pos: { x: number; y: number }) => void;
  onEliminarNodo: (id: string) => void;
  onEliminarArista: (id: string) => void;
}

export function CanvasEditor({ nodos, aristas, nodosConValor, onMoverNodo, onEliminarNodo, onEliminarArista }: Props) {
  const svgRef        = useRef<SVGSVGElement>(null);
  const posRef        = useRef<Record<string, { x: number; y: number }>>({});
  const draggingRef   = useRef<{ id: string; ox: number; oy: number } | null>(null);

  useEffect(() => {
    posRef.current = Object.fromEntries(nodos.map(n => [n.id, n.posicion]));
  }, [nodos]);

  useEffect(() => {
    const svg = svgRef.current;
    if (!svg) return;
    const onMove = (e: MouseEvent) => {
      if (!draggingRef.current) return;
      const rect = svg.getBoundingClientRect();
      const sx   = svg.viewBox.baseVal.width  / rect.width;
      const sy   = svg.viewBox.baseVal.height / rect.height;
      const nx   = (e.clientX - rect.left) * sx - draggingRef.current.ox;
      const ny   = (e.clientY - rect.top)  * sy - draggingRef.current.oy;
      posRef.current[draggingRef.current.id] = { x: nx, y: ny };
      svg.querySelector<SVGGElement>(`[data-nid="${draggingRef.current.id}"]`)
         ?.setAttribute('transform', `translate(${nx},${ny})`);
    };
    const onUp = () => {
      if (!draggingRef.current) return;
      const { id } = draggingRef.current;
      draggingRef.current = null;
      onMoverNodo(id, posRef.current[id] ?? { x: 0, y: 0 });
    };
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup',   onUp);
    return () => { window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp); };
  }, [onMoverNodo]);

  const onNodoDown = useCallback((e: React.MouseEvent, id: string) => {
    e.preventDefault();
    const svg = svgRef.current; if (!svg) return;
    const rect = svg.getBoundingClientRect();
    const sx   = svg.viewBox.baseVal.width  / rect.width;
    const sy   = svg.viewBox.baseVal.height / rect.height;
    const pos  = posRef.current[id] ?? { x: 0, y: 0 };
    draggingRef.current = { id, ox: (e.clientX - rect.left) * sx - pos.x, oy: (e.clientY - rect.top) * sy - pos.y };
  }, []);

  const valMap: Record<string, ValorBelnap> = {};
  if (nodosConValor) for (const n of nodosConValor) valMap[n.id] = n.valorActual;
  const enSim = (nodosConValor?.length ?? 0) > 0;

  return (
    <svg ref={svgRef} viewBox="0 0 860 520"
      style={{ width: '100%', background: PALETA.elevado, borderRadius: 16, display: 'block', minHeight: 340 }}>
      <defs>
        <marker id="arr" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
          <polygon points="0 0,10 3.5,0 7" fill="#475569" />
        </marker>
        {enSim && nodos.map(n => (
          <marker key={`m-${n.id}`} id={`a-${n.id}`} markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0,10 3.5,0 7" fill={COLOR_BELNAP[valMap[n.id] ?? 'N']} />
          </marker>
        ))}
      </defs>

      {/* Aristas */}
      {aristas.map(a => {
        const o = nodos.find(n => n.id === a.idOrigen);
        const d = nodos.find(n => n.id === a.idDestino);
        if (!o || !d) return null;
        const color = enSim ? COLOR_BELNAP[valMap[a.idOrigen] ?? 'N'] : '#475569';
        const mid   = enSim ? `a-${a.idOrigen}` : 'arr';
        const dx = d.posicion.x - o.posicion.x, dy = d.posicion.y - o.posicion.y;
        const len = Math.sqrt(dx*dx + dy*dy) || 1;
        const x1 = o.posicion.x + dx/len*R,      y1 = o.posicion.y + dy/len*R;
        const x2 = d.posicion.x - dx/len*(R+8),  y2 = d.posicion.y - dy/len*(R+8);
        return (
          <g key={a.id} style={{ cursor: 'pointer' }} onClick={() => onEliminarArista(a.id)}>
            <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={color} strokeWidth={enSim ? 3 : 2}
              markerEnd={`url(#${mid})`}
              strokeDasharray={enSim ? '8 4' : undefined}
              style={enSim ? { animation: 'flujo 0.8s linear infinite' } : undefined} />
            <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="transparent" strokeWidth={14} />
          </g>
        );
      })}

      {/* Nodos */}
      {nodos.map(n => {
        const val    = valMap[n.id] ?? 'N';
        const fill   = enSim ? COLOR_BELNAP[val] : (n.tipo === 'premisa' ? '#2d3a5a' : PALETA.tarjeta);
        const stroke = n.tipo === 'premisa' ? '#f59e0b' : (enSim ? COLOR_BELNAP[val] : PALETA.acento);
        return (
          <g key={n.id} data-nid={n.id} transform={`translate(${n.posicion.x},${n.posicion.y})`}
            style={{ cursor: 'grab', userSelect: 'none' }}
            onMouseDown={e => onNodoDown(e, n.id)}
            onDoubleClick={() => onEliminarNodo(n.id)}>
            <circle r={R} fill={fill} stroke={stroke} strokeWidth={n.tipo === 'premisa' ? 3 : 2} />
            {/* Forma: rombo para premisas, círculo para operadores */}
            {n.tipo === 'premisa' && (
              <polygon points={`0,${-R+6} ${R-6},0 0,${R-6} ${-(R-6)},0`}
                fill="none" stroke="#f59e0b" strokeWidth={1} opacity={0.4} />
            )}
            {/* Tipo / valor */}
            <text textAnchor="middle" dominantBaseline="middle" y={enSim ? -8 : 0}
              fill="white" fontSize={n.tipo === 'premisa' ? 20 : 13} fontWeight="bold"
              style={{ pointerEvents: 'none' }}>
              {n.tipo === 'premisa' ? (enSim ? ETIQ_BELNAP[val] : (n.propiedades.valor ?? 'T')) : n.tipo}
            </text>
            {enSim && n.tipo !== 'premisa' && (
              <text textAnchor="middle" dominantBaseline="middle" y={9}
                fill="white" fontSize={13} fontWeight="bold" style={{ pointerEvents: 'none' }}>
                {val}
              </text>
            )}
            {enSim && (
              <text textAnchor="middle" dominantBaseline="middle" y={R + 13}
                fill={COLOR_BELNAP[val]} fontSize={10} style={{ pointerEvents: 'none' }}>
                {DESC_BELNAP[val]}
              </text>
            )}
            {/* Etiqueta */}
            <text textAnchor="middle" dominantBaseline="middle" y={enSim ? R + 26 : R + 16}
              fill="#cbd5e1" fontSize={11} style={{ pointerEvents: 'none' }}>
              {n.etiqueta}
            </text>
            {n.tipo === 'premisa' && !enSim && (
              <text textAnchor="middle" y={-(R + 12)} fill="#f59e0b" fontSize={10} fontWeight="bold"
                style={{ pointerEvents: 'none' }}>★ premisa</text>
            )}
          </g>
        );
      })}

      {nodos.length === 0 && (
        <text x={430} y={260} textAnchor="middle" fill="#334155" fontSize={15}>
          Agrega nodos con el panel de la derecha
        </text>
      )}
      <style>{`@keyframes flujo{from{stroke-dashoffset:24}to{stroke-dashoffset:0}}`}</style>
    </svg>
  );
}
