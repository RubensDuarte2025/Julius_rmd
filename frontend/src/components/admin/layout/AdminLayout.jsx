import React from 'react';
import { Outlet } from 'react-router-dom';
import AdminSidebar from './AdminSidebar';

const AdminLayout = () => {
  const layoutStyle = {
    display: 'flex',
    minHeight: '100vh', // Garante que o layout ocupe toda a altura da tela
  };

  const mainContentStyle = {
    flexGrow: 1, // Permite que o conteúdo principal ocupe o espaço restante
    padding: '20px',
    backgroundColor: '#ffffff', // Fundo branco para a área de conteúdo
    overflowY: 'auto', // Scroll se o conteúdo for maior que a tela
  };

  return (
    <div style={layoutStyle}>
      <AdminSidebar />
      <main style={mainContentStyle}>
        <Outlet /> {/* Rotas filhas do admin serão renderizadas aqui */}
      </main>
    </div>
  );
};

export default AdminLayout;
