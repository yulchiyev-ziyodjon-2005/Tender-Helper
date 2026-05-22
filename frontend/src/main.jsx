/**
 * TenderHelper AI — Entry Point
 * ================================
 * React ilovasining boshlang'ich nuqtasi.
 * i18n (ko'p tillilik) va CSS yuklanadi.
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import './i18n'; // Ko'p tillilik initsializatsiyasi
import './index.css';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>
);
