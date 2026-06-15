/**
 * Toast component for user feedback messages.
 */

import { useEffect, useState } from 'react';

interface ToastProps {
  mensaje: string;
  tipo?: 'error' | 'success' | 'info';
  duracion?: number;
  onCerrar: () => void;
}

export default function Toast({ mensaje, tipo = 'error', duracion = 3000, onCerrar }: ToastProps) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      setTimeout(onCerrar, 300);
    }, duracion);
    return () => clearTimeout(timer);
  }, [duracion, onCerrar]);

  const colores = {
    error: 'bg-red-500/90 border-red-400 text-white',
    success: 'bg-green-500/90 border-green-400 text-white',
    info: 'bg-acento/90 border-acento-light text-white',
  };

  return (
    <div
      className={`
        fixed bottom-6 left-1/2 -translate-x-1/2 z-[100]
        px-4 py-3 rounded-xl border backdrop-blur-md
        text-sm font-medium shadow-xl
        transition-all duration-300
        ${colores[tipo]}
        ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'}
      `}
      role="alert"
      aria-live="assertive"
    >
      {mensaje}
    </div>
  );
}