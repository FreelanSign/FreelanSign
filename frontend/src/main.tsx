import React from 'react';
import ReactDOM from 'react-dom/client';
import AppRouter from './app/router';
import { AuthProvider } from './app/providers/AuthProvider';
import { HelmetProvider } from 'react-helmet-async';

import './styles/index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <HelmetProvider>
      <AuthProvider>
        <AppRouter />
      </AuthProvider>
    </HelmetProvider>
  </React.StrictMode>,
);
