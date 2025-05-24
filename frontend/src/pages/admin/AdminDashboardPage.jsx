import React from 'react';
import { Link } from 'react-router-dom';

const AdminDashboardPage = () => {
  const pageStyle = {
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
  };

  const headerStyle = {
    borderBottom: '1px solid #eee',
    paddingBottom: '10px',
    marginBottom: '20px',
  };

  const quickLinksContainerStyle = {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '15px', // Espaçamento entre os links
  };

  const linkCardStyle = {
    backgroundColor: '#f8f9fa',
    border: '1px solid #dee2e6',
    borderRadius: '8px',
    padding: '20px',
    textDecoration: 'none',
    color: '#212529',
    width: '200px', // Largura fixa para os cards de link
    textAlign: 'center',
    boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
    transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
  };

  const linkCardHoverStyle = (e) => {
    e.currentTarget.style.transform = 'translateY(-3px)';
    e.currentTarget.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
  };

  const linkCardLeaveStyle = (e) => {
    e.currentTarget.style.transform = 'translateY(0)';
    e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
  };
  
  const linkTitleStyle = {
    fontSize: '1.1em',
    fontWeight: 'bold',
    marginBottom: '8px',
  };

  const linkDescriptionStyle = {
    fontSize: '0.9em',
    color: '#6c757d',
  };

  const links = [
    { to: "/admin/cardapio/categorias", title: "Categorias", description: "Gerenciar categorias de produtos." },
    { to: "/admin/cardapio/produtos", title: "Produtos", description: "Adicionar e editar produtos." },
    { to: "/admin/mesas", title: "Mesas", description: "Configurar mesas do restaurante." },
    { to: "/admin/configuracoes", title: "Configurações", description: "Ajustar configurações gerais." },
    { to: "/admin/relatorios/vendas", title: "Relatório de Vendas", description: "Visualizar vendas." },
    { to: "/admin/relatorios/produtos", title: "Relatório de Produtos", description: "Produtos mais vendidos." },
  ];

  return (
    <div style={pageStyle}>
      <header style={headerStyle}>
        <h2>Dashboard Administrativo</h2>
      </header>
      <p>Bem-vindo ao painel de administração. Use os links abaixo ou a barra lateral para navegar.</p>
      
      <div style={quickLinksContainerStyle}>
        {links.map(link => (
          <Link 
            key={link.to} 
            to={link.to} 
            style={linkCardStyle}
            onMouseEnter={linkCardHoverStyle}
            onMouseLeave={linkCardLeaveStyle}
          >
            <div style={linkTitleStyle}>{link.title}</div>
            <div style={linkDescriptionStyle}>{link.description}</div>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default AdminDashboardPage;
