import React from 'react';

const DetalhesPedidoMesa = ({ pedido, onRemoverItem }) => {
  if (!pedido || !pedido.itens_pedido || pedido.itens_pedido.length === 0) {
    return <p>Nenhum item no pedido ainda.</p>;
  }

  const containerStyle = {
    marginTop: '20px',
    padding: '15px',
    border: '1px solid #eee',
    borderRadius: '5px',
    backgroundColor: '#f9f9f9',
  };

  const listStyle = {
    listStyleType: 'none',
    padding: 0,
  };

  const listItemStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '8px 0',
    borderBottom: '1px dotted #ddd',
  };

  const totalStyle = {
    marginTop: '15px',
    paddingTop: '10px',
    borderTop: '2px solid #333',
    fontWeight: 'bold',
    fontSize: '1.1em',
    display: 'flex',
    justifyContent: 'space-between',
  };

  const calcularTotalPedido = () => {
    if (pedido && pedido.itens_pedido) {
      return pedido.itens_pedido.reduce((acc, item) => acc + parseFloat(item.subtotal_item || 0), 0);
    }
    return 0;
  };
  
  // Backend já envia `total_pedido` calculado, mas podemos recalcular se necessário ou para validação.
  // const totalCalculado = calcularTotalPedido();
  const totalExibido = pedido.total_pedido ? parseFloat(pedido.total_pedido).toFixed(2) : calcularTotalPedido().toFixed(2);


  return (
    <div style={containerStyle}>
      <h4>Itens do Pedido #{pedido.id}</h4>
      <ul style={listStyle}>
        {pedido.itens_pedido.map((item) => (
          <li key={item.id} style={listItemStyle}>
            <span>
              {item.quantidade}x {item.produto?.nome || 'Produto não carregado'} 
              {item.observacoes_item ? ` (${item.observacoes_item})` : ''}
            </span>
            <span>R$ {parseFloat(item.subtotal_item || 0).toFixed(2)}</span>
            {/* Botão de remover item (Pós-MVP, mas a função onRemoverItem está prevista) */}
            {onRemoverItem && (
                 <button 
                    onClick={() => onRemoverItem(item.id)} 
                    style={{ marginLeft: '10px', color: 'red', background: 'none', border: 'none', cursor: 'pointer' }}
                    title="Remover Item"
                >
                    &times;
                </button>
            )}
          </li>
        ))}
      </ul>
      <div style={totalStyle}>
        <span>Total do Pedido:</span>
        <span>R$ {totalExibido}</span>
      </div>
      {pedido.status_pedido && <p style={{ marginTop: '10px', fontStyle: 'italic' }}>Status: {pedido.status_pedido}</p>}
    </div>
  );
};

export default DetalhesPedidoMesa;
