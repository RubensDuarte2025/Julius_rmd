import React, { useState } from 'react';
import cozinhaService from '../../services/cozinhaService';
import ItemPedidoCozinhaView from './ItemPedidoCozinhaView';

const PedidoCozinhaCard = ({ pedido, onAtualizarStatus }) => {
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState(null);

  if (!pedido) {
    return null;
  }

  const handleUpdateStatus = async (novoStatus) => {
    setIsUpdating(true);
    setError(null);
    try {
      await cozinhaService.atualizarStatusPedidoCozinha(
        pedido.tipo_origem,
        pedido.id_pedido_origem,
        novoStatus
      );
      if (onAtualizarStatus) {
        onAtualizarStatus(pedido.id_pedido_origem, pedido.tipo_origem, novoStatus);
      }
    } catch (err) {
      console.error("Erro ao atualizar status do pedido na cozinha:", err);
      setError(err.response?.data?.detail || "Falha ao atualizar status.");
      // Manter o estado de updating como false para permitir nova tentativa
      setIsUpdating(false); 
      // Poderia ter um timeout para limpar o erro
      setTimeout(() => setError(null), 5000);
      return; // Não prosseguir se houver erro
    }
    // Não é necessário setIsUpdating(false) aqui se o componente for removido/recarregado
    // Mas se ele persistir, é bom resetar.
    // Para MVP, onde a lista pode ser re-feita, o componente pode sumir.
  };

  const getCardStyle = () => {
    let backgroundColor = '#fff'; // Default
    let borderColor = '#ddd';
    if (pedido.status_cozinha_atual === 'EmPreparo') {
      backgroundColor = '#fff3cd'; // Amarelo claro (Bootstrap 'warning' light)
      borderColor = '#ffeeba';
    } else if (pedido.status_cozinha_atual === 'AguardandoPreparo') {
      backgroundColor = '#f8f9fa'; // Cinza claro
    }
    // Pedidos 'Pronto' são geralmente removidos da lista principal no dashboard,
    // mas se fossem exibidos, poderiam ter outra cor (ex: verde claro).

    return {
      border: `2px solid ${borderColor}`,
      borderRadius: '8px',
      padding: '15px',
      margin: '10px',
      backgroundColor: backgroundColor,
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      width: '300px', // Largura fixa para consistência em uma lista
      display: 'flex',
      flexDirection: 'column',
    };
  };

  const headerStyle = {
    borderBottom: '1px solid #eee',
    paddingBottom: '10px',
    marginBottom: '10px',
  };

  const titleStyle = {
    margin: '0 0 5px 0',
    fontSize: '1.2em',
  };
  
  const detailStyle = {
    fontSize: '0.9em',
    color: '#555',
    marginBottom: '3px',
  };

  const itemsContainerStyle = {
    marginBottom: '15px',
  };
  
  const buttonContainerStyle = {
    marginTop: 'auto', // Empurra botões para o final do card
    paddingTop: '10px',
    borderTop: '1px solid #eee',
    display: 'flex',
    justifyContent: 'space-around', // Ou 'flex-end'
  };

  const buttonStyle = {
    padding: '8px 12px',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontWeight: 'bold',
    minWidth: '120px', // Largura mínima para botões
  };


  return (
    <div style={getCardStyle()}>
      <div style={headerStyle}>
        <h3 style={titleStyle}>
          Pedido: {pedido.identificador_cliente} ({pedido.tipo_origem})
        </h3>
        <p style={detailStyle}>ID: {pedido.id_pedido_origem}-{pedido.tipo_origem.charAt(0)}</p>
        <p style={detailStyle}>
          Entrada: {new Date(pedido.horario_entrada_cozinha).toLocaleTimeString()}
        </p>
        <p style={detailStyle}>Status: <strong>{pedido.status_cozinha_atual}</strong></p>
      </div>

      <div style={itemsContainerStyle}>
        <h4>Itens:</h4>
        {pedido.itens && pedido.itens.length > 0 ? (
          pedido.itens.map((item, index) => (
            // Usar um ID único para o item se disponível, senão o índice
            <ItemPedidoCozinhaView key={item.id || index} item={item} />
          ))
        ) : (
          <p>Nenhum item listado para este pedido.</p>
        )}
      </div>

      {error && <p style={{ color: 'red', fontStyle: 'italic', fontSize: '0.9em' }}>Erro: {error}</p>}

      <div style={buttonContainerStyle}>
        {pedido.status_cozinha_atual === 'AguardandoPreparo' && (
          <button
            onClick={() => handleUpdateStatus('EmPreparo')}
            disabled={isUpdating}
            style={{...buttonStyle, backgroundColor: '#ffc107', color: '#333'}}
          >
            {isUpdating ? 'Marcando...' : 'Marcar Em Preparo'}
          </button>
        )}
        {pedido.status_cozinha_atual === 'EmPreparo' && (
          <button
            onClick={() => handleUpdateStatus('Pronto')}
            disabled={isUpdating}
            style={{...buttonStyle, backgroundColor: '#28a745', color: 'white'}}
          >
            {isUpdating ? 'Marcando...' : 'Marcar Pronto'}
          </button>
        )}
      </div>
    </div>
  );
};

export default PedidoCozinhaCard;
