/**
 * FormularioNodo.tsx — Formulario para agregar un nodo.
 *
 * Si el usuario marca "Premisa": solo puede asignar un valor T/F/B/N.
 * Si NO es premisa: solo puede elegir un operador AND/OR/XOR/NOT.
 * Esto refleja exactamente el dominio EPiC del proyecto.
 */

import { useState, useRef } from 'react';
import type { Nodo, ValorBelnap, OperadorLogico } from '../compartido/tipos';
import { COLOR_BELNAP, DESC_BELNAP } from '../compartido/constantes';

const SIMBOLOS = ['¬', '∧', '∨', '→', '↔', '∴', '⊥', '⊤', '∀', '∃'];

const VALORES: ValorBelnap[]   = ['T', 'F', 'B', 'N'];
const OPERADORES: { op: OperadorLogico; desc: string }[] = [
  { op: 'OR',  desc: 'OR  — verdadero si al menos 1 entrada es T' },
  { op: 'AND', desc: 'AND — verdadero si TODAS las entradas son T' },
  { op: 'XOR', desc: 'XOR — verdadero si EXACTAMENTE 1 entrada es T' },
  { op: 'MT',  desc: 'MT — Modus Tollens: de (A→B) y ¬B produce ¬A  (2 entradas en orden)' },
  { op: 'IMP', desc: 'IMP — Implicación a→b  (2 entradas: antecedente, consecuente)' },
  { op: 'NOT', desc: 'NOT — invierte la única entrada (requiere 1 entrada)' },
];

interface Props {
  cantidadNodos: number;
  onAgregar: (nodo: Nodo) => void;
}

export function FormularioNodo({ cantidadNodos, onAgregar }: Props) {
  const [etiqueta,    setEtiqueta]    = useState('');
  const [esPremisa,   setEsPremisa]   = useState(false);
  const [valor,       setValor]       = useState<ValorBelnap>('T');
  const [operador,    setOperador]    = useState<OperadorLogico>('OR');
  const inputRef = useRef<HTMLInputElement>(null);

  const insertar = (sym: string) => {
    const el = inputRef.current;
    if (!el) return;
    const s   = el.selectionStart ?? etiqueta.length;
    const e   = el.selectionEnd   ?? etiqueta.length;
    const nuevo = etiqueta.slice(0, s) + sym + etiqueta.slice(e);
    setEtiqueta(nuevo);
    requestAnimationFrame(() => {
      el.focus();
      el.setSelectionRange(s + sym.length, s + sym.length);
    });
  };

  const submit = () => {
    const idx    = cantidadNodos + 1;
    const label  = etiqueta.trim() || (esPremisa ? `P${idx}` : `N${idx}`);
    const nodo: Nodo = esPremisa
      ? {
          id: `nodo-${String(idx).padStart(3, '0')}`,
          etiqueta: label,
          tipo: 'premisa',
          propiedades: { valor },
          posicion: { x: 80 + (idx % 3) * 240, y: 100 + Math.floor(idx / 3) * 180 },
        }
      : {
          id: `nodo-${String(idx).padStart(3, '0')}`,
          etiqueta: label,
          tipo: operador,
          propiedades: {},
          posicion: { x: 80 + (idx % 3) * 240, y: 100 + Math.floor(idx / 3) * 180 },
        };
    onAgregar(nodo);
    setEtiqueta('');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>

      {/* Etiqueta */}
      <label style={labelSt}>Etiqueta</label>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginBottom: 2 }}>
        {SIMBOLOS.map(s => (
          <button key={s} onClick={() => insertar(s)} style={btnSymSt}>{s}</button>
        ))}
      </div>
      <input
        ref={inputRef}
        value={etiqueta}
        onChange={e => setEtiqueta(e.target.value)}
        placeholder={esPremisa ? 'ej. P, Hipótesis A' : 'ej. P ∧ Q, Conclusión'}
        style={inputSt}
        onKeyDown={e => e.key === 'Enter' && submit()}
      />

      {/* Toggle premisa / operador */}
      <div style={{ display: 'flex', background: '#0f1f3d', borderRadius: 8, padding: 3 }}>
        <button
          onClick={() => setEsPremisa(true)}
          style={{ flex: 1, background: esPremisa ? '#f59e0b' : 'transparent', border: 'none',
            color: esPremisa ? '#0f1f3d' : '#94a3b8', borderRadius: 6, padding: '6px 0',
            fontSize: 12, fontWeight: esPremisa ? 700 : 400, cursor: 'pointer' }}>
          ★ Premisa
        </button>
        <button
          onClick={() => setEsPremisa(false)}
          style={{ flex: 1, background: !esPremisa ? '#6366f1' : 'transparent', border: 'none',
            color: !esPremisa ? 'white' : '#94a3b8', borderRadius: 6, padding: '6px 0',
            fontSize: 12, fontWeight: !esPremisa ? 700 : 400, cursor: 'pointer' }}>
          ⊕ Operador
        </button>
      </div>

      {/* Premisa: selector de valor T/F/B/N */}
      {esPremisa && (
        <>
          <label style={labelSt}>Valor evidencial de la premisa</label>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6 }}>
            {VALORES.map(v => (
              <button key={v} onClick={() => setValor(v)} style={{
                background: valor === v ? COLOR_BELNAP[v] : '#0f1f3d',
                border: `2px solid ${valor === v ? COLOR_BELNAP[v] : '#1e3a5f'}`,
                color: valor === v ? 'white' : '#94a3b8',
                borderRadius: 8, padding: '8px 4px', cursor: 'pointer',
                fontSize: 12, fontWeight: valor === v ? 700 : 400,
              }}>
                <span style={{ fontSize: 16, display: 'block' }}>{v}</span>
                <span style={{ fontSize: 10 }}>{DESC_BELNAP[v]}</span>
              </button>
            ))}
          </div>
        </>
      )}

      {/* Operador: selector AND/OR/XOR/NOT */}
      {!esPremisa && (
        <>
          <label style={labelSt}>Operador lógico</label>
          {OPERADORES.map(({ op, desc }) => (
            <button key={op} onClick={() => setOperador(op)} style={{
              background: operador === op ? '#6366f1' : '#0f1f3d',
              border: `1px solid ${operador === op ? '#6366f1' : '#1e3a5f'}`,
              color: 'white', borderRadius: 8, padding: '8px 10px',
              cursor: 'pointer', textAlign: 'left', fontSize: 12,
              fontWeight: operador === op ? 700 : 400,
            }}>
              <strong style={{ color: operador === op ? 'white' : '#818cf8' }}>{op}</strong>
              <span style={{ color: '#94a3b8', marginLeft: 6 }}>{desc.split('—')[1]?.trim()}</span>
            </button>
          ))}
        </>
      )}

      <button onClick={submit} style={btnPriSt}>
        + Agregar {esPremisa ? 'premisa' : 'operador'}
      </button>
    </div>
  );
}

const labelSt: React.CSSProperties = { fontSize: 12, color: '#94a3b8' };
const inputSt: React.CSSProperties = {
  background: '#0f1f3d', border: '1px solid #1e3a5f', color: 'white',
  borderRadius: 8, padding: '7px 10px', fontSize: 13, outline: 'none', width: '100%',
};
const btnSymSt: React.CSSProperties = {
  background: '#1e3a5f', border: 'none', color: '#93c5fd',
  borderRadius: 6, padding: '3px 8px', fontSize: 14, cursor: 'pointer',
};
const btnPriSt: React.CSSProperties = {
  background: '#6366f1', border: 'none', color: 'white',
  borderRadius: 8, padding: '9px 0', fontSize: 13, fontWeight: 'bold', cursor: 'pointer',
};
