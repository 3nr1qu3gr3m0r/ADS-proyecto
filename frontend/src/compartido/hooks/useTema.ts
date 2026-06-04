/**
 * Prompt: "Hook para alternar tema oscuro/claro con
 * persistencia en localStorage y respeto a la media query
 * prefers-color-scheme. Establece data-theme en <html>."
 */

import { useState, useCallback, useEffect } from 'react';

export type Tema = 'dark' | 'light';

const STORAGE_KEY = 'epic-tema';

export function useTema() {
  const [tema, setTema] = useState<Tema>(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === 'dark' || stored === 'light') return stored;
    return window.matchMedia('(prefers-color-scheme:light)').matches ? 'light' : 'dark';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', tema);
    localStorage.setItem(STORAGE_KEY, tema);
  }, [tema]);

  const toggle = useCallback(() => {
    setTema((t) => (t === 'dark' ? 'light' : 'dark'));
  }, []);

  return { tema, toggle };
}