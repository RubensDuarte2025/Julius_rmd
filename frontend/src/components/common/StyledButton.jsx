import React from 'react';
import Button from '@mui/material/Button';
import { CircularProgress } from '@mui/material'; // Para feedback de loading

const StyledButton = ({ children, loading, ...props }) => {
  return (
    <Button 
      variant="contained" // Estilo padrão para botões principais
      disabled={loading} // Desabilitar botão durante o loading
      {...props} // Permite passar outras props do MUI Button (ex: color, onClick, size)
      sx={{ // Adicionar estilizações customizadas via sx prop se necessário
        // Exemplo: textTransform: 'none', // Para não ter botões em maiúsculas
        // Exemplo: margin: '5px',
        ...(props.sx || {}) // Mantém quaisquer sx props passadas
      }}
    >
      {loading ? <CircularProgress size={24} color="inherit" /> : children}
    </Button>
  );
};

export default StyledButton;
