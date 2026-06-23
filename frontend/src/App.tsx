// ============ PROMPT ============
// Implementa el componente raíz de EPiC Playground: un editor visual de grafos
// lógicos con canvas SVG interactivo, formularios para crear nodos (premisa/operador)
// y aristas, simulación paso a paso con navegación local del historial de propagación
// y visualización de valores Belnap (T/F/B/N) codificados por colores semánticos.
// ======== FIN DEL PROMPT ========

/**
 * App.tsx — EPiC Playground.
 *
 * Navegación del historial completamente LOCAL:
 * el backend ya devuelve todos los pasos en la respuesta inicial de
 * iniciarSimulacion. No se necesita llamar a avanzar/retroceder en el
 * backend para moverse entre iteraciones; basta con mover pasoVisible.
 *
 * Por defecto se muestra el ÚLTIMO paso (resultado convergido), y el
 * usuario puede retroceder para ver cómo se propagaron los valores.
 */

import { useState, useRef, useCallback, useEffect } from 'react';
import type {
  Nodo, Arista, Red, EstadoSimulacion,
  NodoConValor, FaseSimulacion, ValorBelnap,
} from './compartido/tipos';
import { PRESETS, PALETA, COLOR_BELNAP, DESC_BELNAP } from './compartido/constantes';
import { iniciarSimulacion } from './compartido/api';

import { CanvasEditor }        from './editor/CanvasEditor';
import { FormularioNodo }      from './editor/FormularioNodo';
import { FormularioArista }    from './editor/FormularioArista';
import { ControlesSimulacion } from './visualizador/ControlesSimulacion';
import { PanelResultados }     from './visualizador/PanelResultados';

type Tab = 'editor' | 'resultados';

export default function App() {
  // ── Red ───────────────────────────────────────────────────────────────────
  const [nodos,   setNodos]   = useState<Nodo[]>([]);
  const [aristas, setAristas] = useState<Arista[]>([]);
  const [preset,  setPreset]  = useState('');

  // ── Simulación ───────────────────────────────────────────────────────────
  const [simulacion,  setSimulacion]  = useState<EstadoSimulacion | null>(null);
  const [pasoVisible, setPasoVisible] = useState(0);   // índice local en historial
  const [fase,        setFase]        = useState<FaseSimulacion>('inactivo');
  const [cargando,    setCargando]    = useState(false);
  const [error,       setError]       = useState<string | null>(null);
  const intervaloRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // ── UI ────────────────────────────────────────────────────────────────────
  const [tab, setTab] = useState<Tab>('editor');

  // ── Red helpers ───────────────────────────────────────────────────────────
  const redActual = (): Red => ({ id: preset || 'red-001', nodos, aristas, version: 1 });

  const cargarPreset = (nombre: string) => {
    const p = PRESETS[nombre]; if (!p) return;
    setNodos([...p.nodos]); setAristas([...p.aristas]);
    setPreset(nombre); reiniciar();
  };

  function reiniciar() {
    pararIntervalo();
    setSimulacion(null); setPasoVisible(0);
    setFase('inactivo'); setError(null); setTab('editor');
  }
  function pararIntervalo() {
    if (intervaloRef.current) { clearInterval(intervaloRef.current); intervaloRef.current = null; }
  }

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const agregarNodo   = useCallback((n: Nodo)   => { setNodos(p => [...p, n]);   reiniciar(); }, []);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const agregarArista = useCallback((a: Arista)  => { setAristas(p => [...p, a]); reiniciar(); }, []);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const eliminarNodo  = useCallback((id: string) => {
    setNodos(p   => p.filter(n => n.id !== id));
    setAristas(p => p.filter(a => a.idOrigen !== id && a.idDestino !== id));
    reiniciar();
  }, []);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const eliminarArista = useCallback((id: string) => { setAristas(p => p.filter(a => a.id !== id)); reiniciar(); }, []);
  const moverNodo = useCallback((id: string, pos: { x: number; y: number }) => {
    setNodos(p => p.map(n => n.id === id ? { ...n, posicion: pos } : n));
  }, []);

  // ── Simulación ────────────────────────────────────────────────────────────

  const simular = async () => {
    if (nodos.length === 0) { setError('Agrega al menos un nodo antes de simular.'); return; }
    setCargando(true); setError(null); pararIntervalo();
    try {
      const res = await iniciarSimulacion(redActual());
      setSimulacion(res);
      // ▶ Mostrar DIRECTAMENTE el último paso (resultado convergido)
      setPasoVisible(res.historial.length - 1);
      setFase(res.historial[res.historial.length - 1]?.convergido ? 'completado' : 'error');
      setTab('resultados');
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setCargando(false);
    }
  };

  // Play: recorre el historial desde el paso 0 hasta el final automáticamente
  const handlePlay = () => {
    if (!simulacion) return;
    pararIntervalo();
    setFase('corriendo');
    setPasoVisible(0);   // reinicia la animación desde el inicio
    let paso = 0;
    intervaloRef.current = setInterval(() => {
      paso += 1;
      if (paso >= (simulacion.historial.length)) {
        pararIntervalo();
        setFase('completado');
        setPasoVisible(simulacion.historial.length - 1);
      } else {
        setPasoVisible(paso);
      }
    }, 900);
  };

  const handlePausar = () => {
    pararIntervalo();
    setFase('pausado');
  };

  // Avanzar/Retroceder: navega localmente el historial sin llamar al backend
  const handlePaso = () => {
    pararIntervalo();
    setFase('pausado');
    setPasoVisible(p => Math.min(p + 1, (simulacion?.historial.length ?? 1) - 1));
  };

  const handleRetroceder = () => {
    pararIntervalo();
    setFase('pausado');
    setPasoVisible(p => Math.max(p - 1, 0));
  };

  useEffect(() => () => pararIntervalo(), []);

  // ── Datos del paso visible ────────────────────────────────────────────────

  const resultadoVisible = simulacion?.historial[pasoVisible] ?? null;
  const totalPasos       = simulacion?.historial.length ?? 0;

  const nodosConValor: NodoConValor[] = nodos.map(n => ({
    ...n,
    valorActual: (resultadoVisible?.valoresNodos[n.id] ?? 'N') as ValorBelnap,
  }));

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div style={{ minHeight: '100vh', background: PALETA.fondo, color: '#f1f5f9',
      fontFamily: 'Segoe UI, system-ui, sans-serif' }}>

      {/* Header */}
      <header style={{ height: 64, display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 28px', background: PALETA.header, boxShadow: '0 2px 20px rgba(0,0,0,.5)' }}>
        <h1 style={{ fontSize: 22, fontWeight: 800 }}>
          EPiC <span style={{ color: PALETA.acento }}>Playground</span>
          <span style={{ fontSize: 11, color: '#64748b', fontWeight: 400, marginLeft: 10 }}>
            Lógica de 4 valores · Belnap
          </span>
        </h1>

        {/* Leyenda rápida */}
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          {(['T','F','B','N'] as ValorBelnap[]).map(v => (
            <div key={v} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <div style={{ width: 20, height: 20, borderRadius: '50%', background: COLOR_BELNAP[v],
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 11, fontWeight: 'bold', color: 'white' }}>{v}</div>
              <span style={{ fontSize: 11, color: '#64748b' }}>{DESC_BELNAP[v]}</span>
            </div>
          ))}
        </div>

        {/* Presets */}
        <div style={{ display: 'flex', gap: 6 }}>
          {Object.keys(PRESETS).map(k => (
            <button key={k} onClick={() => cargarPreset(k)} style={{
              background: preset === k ? PALETA.acento : '#162849', border: 'none',
              color: 'white', borderRadius: 8, padding: '5px 12px',
              fontSize: 11, cursor: 'pointer', fontWeight: preset === k ? 700 : 400,
            }}>{k}</button>
          ))}
          <button onClick={() => { setNodos([]); setAristas([]); setPreset(''); reiniciar(); }}
            style={{ background: '#1e293b', border: 'none', color: '#94a3b8',
              borderRadius: 8, padding: '5px 10px', fontSize: 11, cursor: 'pointer' }}>
            ✕ Limpiar
          </button>
        </div>
      </header>

      {/* Error */}
      {error && (
        <div style={{ background: '#450a0a', color: '#fca5a5', padding: '8px 28px', fontSize: 12 }}>
          ⚠ {error}
          <button onClick={() => setError(null)}
            style={{ marginLeft: 10, background: 'none', border: 'none', color: '#f87171', cursor: 'pointer' }}>✕</button>
        </div>
      )}

      {/* Layout principal */}
      <main style={{ display: 'flex', gap: 18, padding: 18,
        height: 'calc(100vh - 64px)', boxSizing: 'border-box' }}>

        {/* Canvas */}
        <div style={{ flex: 3, display: 'flex', flexDirection: 'column', gap: 8 }}>
          <CanvasEditor
            nodos={nodos} aristas={aristas}
            nodosConValor={resultadoVisible ? nodosConValor : undefined}
            onMoverNodo={moverNodo}
            onEliminarNodo={eliminarNodo}
            onEliminarArista={eliminarArista}
          />
          {/* Barra de progreso de iteraciones */}
          {simulacion && totalPasos > 1 && (
            <div style={{ display: 'flex', gap: 4, alignItems: 'center', justifyContent: 'center' }}>
              {simulacion.historial.map((p, i) => (
                <button key={i} onClick={() => { pararIntervalo(); setFase('pausado'); setPasoVisible(i); }}
                  style={{
                    width: 28, height: 28, borderRadius: '50%', border: 'none', cursor: 'pointer',
                    background: i === pasoVisible ? PALETA.acento : '#162849',
                    color: 'white', fontSize: 11, fontWeight: i === pasoVisible ? 700 : 400,
                  }}
                  title={p.iteraciones === 0 ? 'Estado inicial' : `Iteración ${p.iteraciones}${p.convergido ? ' ✓' : ''}`}>
                  {p.iteraciones === 0 ? '0' : p.iteraciones}
                </button>
              ))}
              <span style={{ fontSize: 10, color: '#334155', marginLeft: 4 }}>
                {resultadoVisible?.iteraciones === 0
                  ? 'Estado inicial (antes de propagar)'
                  : resultadoVisible?.convergido
                    ? `Iteración ${resultadoVisible.iteraciones} — punto fijo ✓`
                    : `Iteración ${resultadoVisible?.iteraciones}`}
              </span>
            </div>
          )}
          <div style={{ fontSize: 10, color: '#1e293b', textAlign: 'center' }}>
            Arrastra nodos · Doble clic elimina nodo · Clic en arista la elimina
          </div>
        </div>

        {/* Panel derecho */}
        <aside style={{ width: 300, display: 'flex', flexDirection: 'column', gap: 12, overflowY: 'auto' }}>

          {/* Tabs */}
          <div style={{ display: 'flex', background: '#0f1f3d', borderRadius: 10, padding: 4 }}>
            {(['editor', 'resultados'] as Tab[]).map(t => (
              <button key={t} onClick={() => setTab(t)} style={{
                flex: 1, background: tab === t ? PALETA.acento : 'transparent',
                border: 'none', color: 'white', borderRadius: 7, padding: '6px 0',
                fontSize: 12, fontWeight: tab === t ? 700 : 400, cursor: 'pointer',
              }}>{t === 'editor' ? '✏ Editor' : '📊 Simulación'}</button>
            ))}
          </div>

          {tab === 'editor' && (
            <>
              <Section titulo="Agregar nodo">
                <FormularioNodo cantidadNodos={nodos.length} onAgregar={agregarNodo} />
              </Section>
              <Section titulo="Conectar nodos">
                <FormularioArista nodos={nodos} cantidadAristas={aristas.length} onAgregar={agregarArista} />
              </Section>
              {nodos.length > 0 && (
                <Section titulo={`Red: ${nodos.length} nodos, ${aristas.length} aristas`}>
                  {nodos.map(n => (
                    <div key={n.id} style={{ display: 'flex', justifyContent: 'space-between',
                      alignItems: 'center', padding: '4px 0', borderBottom: '1px solid #1e293b' }}>
                      <span style={{ fontSize: 12, color: '#cbd5e1' }}>
                        {n.tipo === 'premisa'
                          ? <><span style={{ color: '#f59e0b' }}>★</span> {n.etiqueta} = <span
                              style={{ color: COLOR_BELNAP[(n.propiedades.valor ?? 'T') as ValorBelnap],
                                fontWeight: 'bold' }}>{n.propiedades.valor ?? 'T'}</span></>
                          : <><span style={{ color: '#818cf8', fontWeight: 700 }}>{n.tipo}</span> {n.etiqueta}</>
                        }
                      </span>
                      <button onClick={() => eliminarNodo(n.id)}
                        style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }}>✕</button>
                    </div>
                  ))}
                </Section>
              )}
              <button onClick={simular} disabled={cargando || nodos.length === 0} style={{
                background: PALETA.acento, border: 'none', color: 'white', borderRadius: 10,
                padding: '12px 0', fontSize: 14, fontWeight: 700, cursor: 'pointer',
                opacity: nodos.length === 0 ? 0.4 : 1,
              }}>
                {cargando ? '⏳ Calculando...' : '▶ Simular red'}
              </button>
            </>
          )}

          {tab === 'resultados' && (
            <>
              <Section titulo="Controles">
                <ControlesSimulacion
                  fase={fase}
                  pasoActual={pasoVisible}
                  totalPasos={totalPasos}
                  cargando={cargando}
                  onSimular={simular}
                  onPlay={handlePlay}
                  onPausar={handlePausar}
                  onPaso={handlePaso}
                  onRetroceder={handleRetroceder}
                  onReiniciar={reiniciar}
                />
              </Section>
              {resultadoVisible
                ? <PanelResultados
                    nodos={nodosConValor}
                    iteraciones={resultadoVisible.iteraciones}
                    convergido={resultadoVisible.convergido}
                  />
                : <div style={{ textAlign: 'center', color: '#334155', fontSize: 13, paddingTop: 20 }}>
                    Presiona «▶ Simular red»
                  </div>
              }
            </>
          )}
        </aside>
      </main>
    </div>
  );
}

function Section({ titulo, children }: { titulo: string; children: React.ReactNode }) {
  return (
    <div style={{ background: '#162849', borderRadius: 14, padding: '12px 14px' }}>
      <div style={{ fontSize: 10, color: '#64748b', fontWeight: 700,
        textTransform: 'uppercase', letterSpacing: 1, marginBottom: 10 }}>{titulo}</div>
      {children}
    </div>
  );
}
