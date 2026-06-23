/**
 * FormularioArista.tsx — Formulario para conectar dos nodos.
 *
 * Regla EPiC: las premisas solo pueden ser ORIGEN, nunca DESTINO.
 * Esta restricción se aplica aquí: el dropdown de "destino" no muestra premisas.
 */

import { useState } from 'react';
import type { Nodo, Arista } from '../compartido/tipos';

interface Props {
  nodos: Nodo[];
  cantidadAristas: number;
  onAgregar: (arista: Arista) => void;
}

export function FormularioArista({ nodos, cantidadAristas, onAgregar }: Props) {
  const [origenId,  setOrigenId]  = useState('');
  const [destinoId, setDestinoId] = useState('');

  // Premisas: solo pueden ser origen
  const posiblesOrigen  = nodos;
  const posiblesDestino = nodos.filter(n => n.tipo !== 'premisa' && n.id !== origenId);

  const submit = () => {
    if (!origenId || !destinoId) return;
    const arista: Arista = {
      id: `arista-${String(cantidadAristas + 1).padStart(3, '0')}`,
      idOrigen: origenId,
      idDestino: destinoId,
      peso: 1.0,
      metadatos: {},
    };
    onAgregar(arista);
    setOrigenId('');
    setDestinoId('');
  };

  if (nodos.length < 2) {
    return <p style={{ fontSize: 12, color: '#475569' }}>Agrega al menos 2 nodos para conectarlos.</p>;
  }
  if (posiblesDestino.length === 0) {
    return <p style={{ fontSize: 12, color: '#475569' }}>Necesitas al menos un nodo operador (AND/OR/XOR/NOT) como destino.</p>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>

      <div style={{ background: '#0f1f3d', borderRadius: 8, padding: '6px 10px', fontSize: 11, color: '#64748b' }}>
        ★ Las premisas solo pueden ser <strong style={{ color: '#f59e0b' }}>origen</strong> (de izquierda a derecha)
      </div>

      <label style={labelSt}>Origen (cualquier nodo)</label>
      <select value={origenId} onChange={e => { setOrigenId(e.target.value); setDestinoId(''); }} style={inputSt}>
        <option value="">— Seleccionar —</option>
        {posiblesOrigen.map(n => (
          <option key={n.id} value={n.id}>
            {n.tipo === 'premisa' ? '★ ' : '⊕ '}{n.etiqueta} ({n.id})
          </option>
        ))}
      </select>

      <label style={labelSt}>Destino (solo operadores)</label>
      <select value={destinoId} onChange={e => setDestinoId(e.target.value)} style={inputSt}
        disabled={!origenId}>
        <option value="">— Seleccionar —</option>
        {posiblesDestino.map(n => (
          <option key={n.id} value={n.id}>⊕ {n.etiqueta} ({n.tipo})</option>
        ))}
      </select>

      {origenId && destinoId && nodos.find(n => n.id === destinoId)?.tipo === 'IMP' && (
        <div style={{ background: '#1e3a5f', borderRadius: 8, padding: '6px 10px', fontSize: 11, color: '#93c5fd' }}>
          ℹ IMP: <strong>1ª arista = antecedente (a)</strong>, <strong>2ª = consecuente (b)</strong> → produce a → b
        </div>
      )}

      {origenId && destinoId && nodos.find(n => n.id === destinoId)?.tipo === 'MT' && (
        <div style={{ background: '#1e3a5f', borderRadius: 8, padding: '6px 10px', fontSize: 11, color: '#93c5fd' }}>
          ℹ MT: <strong>1ª arista = la implicación (A→B)</strong>, <strong>2ª = el consecuente (B)</strong> → produce A
        </div>
      )}

      <button
        onClick={submit}
        disabled={!origenId || !destinoId}
        style={{ ...btnSt, opacity: !origenId || !destinoId ? 0.4 : 1 }}>
        → Conectar
      </button>
    </div>
  );
}

const labelSt: React.CSSProperties = { fontSize: 12, color: '#94a3b8' };
const inputSt: React.CSSProperties = {
  background: '#0f1f3d', border: '1px solid #1e3a5f', color: 'white',
  borderRadius: 8, padding: '7px 10px', fontSize: 13, outline: 'none', width: '100%',
};
const btnSt: React.CSSProperties = {
  background: '#6366f1', border: 'none', color: 'white', borderRadius: 8,
  padding: '9px 0', fontSize: 13, fontWeight: 'bold', cursor: 'pointer',
};
