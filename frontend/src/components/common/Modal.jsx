import React from 'react';
import MuiModal from '@mui/material/Modal'; // Renomeado para evitar conflito de nome
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography'; // Para o título
import CloseIcon from '@mui/icons-material/Close';

const modalContentStyle = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: 'auto', // Auto width based on content, or set a specific one
  minWidth: 400, // Minimum width
  maxWidth: '90%', // Max width relative to viewport
  maxHeight: '90vh', // Max height
  overflowY: 'auto', // Scroll for content overflow
  bgcolor: 'background.paper',
  // border: '2px solid #000', // Pode ser removido ou estilizado pelo tema
  borderRadius: '8px', // Usar o borderRadius do tema se possível
  boxShadow: 24,
  p: 3, // Padding interno (MUI spacing units)
};

const ModalHeaderStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  mb: 2, // Margin bottom
};

const Modal = ({ open, onClose, title, children }) => {
  return (
    <MuiModal
      open={open}
      onClose={onClose}
      aria-labelledby="custom-modal-title"
      aria-describedby="custom-modal-description" // Adicionar se houver descrição
    >
      <Box sx={modalContentStyle}>
        <Box sx={ModalHeaderStyle}>
          {title && (
            <Typography id="custom-modal-title" variant="h6" component="h2">
              {title}
            </Typography>
          )}
          <IconButton
            aria-label="close"
            onClick={onClose}
            sx={{ 
              // position: 'absolute', // Não mais absoluto se o header é flex
              // right: 8, 
              // top: 8,
              color: (theme) => theme.palette.grey[500], // Cor do ícone
            }}
          >
            <CloseIcon />
          </IconButton>
        </Box>
        {/* Para a descrição, se necessário */}
        {/* <Typography id="custom-modal-description" sx={{ mb: 2 }}> */}
        {/*   Conteúdo descritivo aqui. */}
        {/* </Typography> */}
        {children}
      </Box>
    </MuiModal>
  );
};

export default Modal;
