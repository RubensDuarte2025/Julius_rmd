import React from 'react';

const ItemPedidoCozinhaView = ({ item }) => {
  if (!item) {
    return null;
  }

  const itemStyle = {
    padding: '8px 0',
    borderBottom: '1px dashed #eee', // Separador leve entre itens
    fontSize: '0.95em',
  };

  const nomeProdutoStyle = {
    fontWeight: 'bold',
  };

  const quantidadeStyle = {
    marginRight: '8px',
    fontWeight: 'bold',
  };

  const observacoesStyle = {
    fontSize: '0.9em',
    color: '#555',
    marginLeft: '10px',
    fontStyle: 'italic',
  };

  return (
    <div style={itemStyle}>
      <span style={quantidadeStyle}>{item.quantidade}x</span>
      <span style={nomeProdutoStyle}>{item.nome_produto || 'Produto não especificado'}</span>
      {item.observacoes_item && (
        <span style={observacoesStyle}>({item.observacoes_item})</span>
      )}
    </div>
  );
};

export default ItemPedidoCozinhaView;
