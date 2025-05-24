import { createTheme } from '@mui/material/styles';

// Define um tema básico para a aplicação.
// Mais customizações podem ser adicionadas conforme a identidade visual for definida.
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', // Um azul padrão do Material Design (Exemplo)
      // light: '#42a5f5',
      // dark: '#1565c0',
      // contrastText: '#fff',
    },
    secondary: {
      main: '#dc004e', // Um rosa/magenta padrão (Exemplo)
      // light: '#ff79b0',
      // dark: '#c51162',
      // contrastText: '#000',
    },
    background: {
      // default: '#f4f6f8', // Um cinza muito claro para o fundo geral
      // paper: '#ffffff',   // Fundo para componentes como Card, Paper
    },
    // error: { main: red.A400 },
    // warning: { main: orange.A400 },
    // info: { main: blue.A400 },
    // success: { main: green.A400 },
  },
  typography: {
    fontFamily: 'Roboto, "Helvetica Neue", Arial, sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 500,
    },
    // Outras customizações de variantes tipográficas (body1, body2, button, caption, etc.)
  },
  shape: {
    borderRadius: 8, // Bordas levemente arredondadas para componentes
  },
  // Customizar espaçamentos, breakpoints, etc.
  // spacing: 8, // (Padrão é 8px)
  // components: { // Override de estilos para componentes específicos do MUI
  //   MuiButton: {
  //     styleOverrides: {
  //       root: {
  //         textTransform: 'none', // Para não ter botões em maiúsculas por padrão
  //       },
  //     },
  //   },
  //   MuiAppBar: {
  //     styleOverrides: {
  //       colorPrimary: {
  //         backgroundColor: '#333', // Exemplo de cor customizada para AppBar
  //       }
  //     }
  //   }
  // },
});

export default theme;
