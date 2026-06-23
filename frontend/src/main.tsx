// ============ PROMPT ============
// Punto de entrada React que monta el componente App dentro de StrictMode
// en el elemento #root del DOM, importando los estilos globales index.css
// que definen las variables CSS del tema oscuro y el reset de Tailwind.
// ======== FIN DEL PROMPT ========

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';

const root = document.getElementById('root');
if (!root) throw new Error('No se encontró el elemento #root');
createRoot(root).render(<StrictMode><App /></StrictMode>);
