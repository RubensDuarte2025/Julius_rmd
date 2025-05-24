import React from 'react';
import { useNavigate } from 'react-router-dom';

// Função auxiliar para determinar a cor baseada no status da mesa
const getStatusColor = (status) => {
  switch (status) {
    case 'Livre':
      return 'lightgreen';
    case 'Ocupada':
      return 'lightcoral';
    case 'AguardandoPagamento':
      return 'lightsalmon';
    case 'Interditada':
      return 'lightgray';
    default:
      return 'white';
  }
};

const MesaCard = ({ mesa }) => {
  const navigate = useNavigate();

  if (!mesa) {
    return null; // Ou algum placeholder se a mesa for nula
  }

  const cardStyle = {
    border: '1px solid #ccc',
    borderRadius: '8px',
    padding: '16px',
    margin: '8px',
    width: '150px',
    textAlign: 'center',
    cursor: 'pointer',
    backgroundColor: getStatusColor(mesa.status),
    boxShadow: '2px 2px 5px rgba(0,0,0,0.1)',
  };

  const handleMesaClick = () => {
    // Navega para a página de operação do pedido para esta mesa.
    // A lógica de criar/buscar pedido ativo será na página de destino.
    navigate(`/atendimento/mesas/${mesa.id}/pedido`);
  };

  return (
    <div style={cardStyle} onClick={handleMesaClick} role="button" tabIndex={0} onKeyPress={handleMesaClick}>
      <h3>Mesa {mesa.numero_identificador}</h3>
      <p>Status: {mesa.status || 'N/A'}</p>
      {/* Poderia exibir informações do pedido ativo se disponíveis e relevantes aqui */}
      {/* Ex: mesa.pedidos_recentes?.[0]?.id ? `Pedido: #${mesa.pedidos_recentes[0].id}` : '' */}
    </div>
  );
};

export default MesaCard;
