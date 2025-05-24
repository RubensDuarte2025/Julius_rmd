import React from 'react';
import ListaMesas from '../../components/atendimento/ListaMesas';

const MesasDashboardPage = () => {
  const pageStyle = {
    padding: '20px',
    fontFamily: 'Arial, sans-serif', // Exemplo de fonte
  };

  const headerStyle = {
    textAlign: 'center',
    marginBottom: '30px',
    color: '#333',
  };

  return (
    <div style={pageStyle}>
      <header style={headerStyle}>
        <h1>Painel de Atendimento - Mesas</h1>
        <p>Selecione uma mesa para iniciar ou continuar um atendimento.</p>
      </header>
      <ListaMesas />
      {/* Outros elementos do dashboard poderiam ser adicionados aqui,
          como um resumo geral ou links rápidos. */}
    </div>
  );
};

export default MesasDashboardPage;
