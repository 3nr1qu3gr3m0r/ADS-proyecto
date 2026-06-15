/**
 * Prompt: "Componente Tooltip con vidrio esmerilado, retardo
 * de 400ms para mostrar, color fijo #e4e4e7. Aparece arriba
 * del elemento hijo centrado."
 */

import { useState, useRef } from 'react';

interface TooltipProps {
  text: string;
  children: React.ReactNode;
}

export default function Tooltip({ text, children }: TooltipProps) {
  const [visible, setVisible] = useState(false);
  const timeoutRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  const show = () => {
    clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => setVisible(true), 400);
  };

  const hide = () => {
    clearTimeout(timeoutRef.current);
    setVisible(false);
  };

  return (
    <div className="relative inline-flex" onMouseEnter={show} onMouseLeave={hide}>
      {children}
      {visible && (
        <span
          className="
            absolute -top-8 left-1/2 -translate-x-1/2
            whitespace-nowrap px-2 py-1 rounded text-xs
            bg-black/80 text-[#e4e4e7]
            backdrop-blur-sm border border-white/10
            pointer-events-none z-50 animate-fade-in
          "
        >
          {text}
        </span>
      )}
    </div>
  );
}