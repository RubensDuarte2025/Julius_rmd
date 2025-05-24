import React from 'react';
import TextField from '@mui/material/TextField';

const StyledInput = React.forwardRef(({
  variant = "outlined", // Default MUI TextField variant
  margin = "normal",    // Default MUI TextField margin
  ...props 
}, ref) => {
  return (
    <TextField
      variant={variant}
      margin={margin}
      fullWidth // Comum para inputs em formulários
      inputRef={ref} // Encaminha a ref, se necessário
      {...props} // Permite passar outras props do MUI TextField (ex: label, type, value, onChange, error, helperText)
      // sx prop pode ser usada para customizações ad-hoc
      // sx={{ 
      //   marginBottom: 2, // Exemplo de espaçamento customizado
      //   ...(props.sx || {}) 
      // }}
    />
  );
});

StyledInput.displayName = 'StyledInput';

export default StyledInput;
