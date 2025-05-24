import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline'; // Para normalização de CSS
import theme from './theme'; // Importa o tema customizado
import './index.css'; // Mantém CSS global se houver (ex: fontes importadas)

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline /> {/* Aplica resets e estilos base do MUI */}
      <App />
    </ThemeProvider>
  </StrictMode>,
);
