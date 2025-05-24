import React, { useState, useEffect } from 'react';
import atendimentoService from '../../services/atendimentoService'; // Para buscar produtos

const AdicionarItemForm = ({ pedidoId, onItemAdicionado }) => {
  const [produtos, setProdutos] = useState([]);
  const [produtoSelecionadoId, setProdutoSelecionadoId] = useState('');
  const [quantidade, setQuantidade] = useState(1);
  const [observacoes, setObservacoes] = useState('');
  const [isLoadingProdutos, setIsLoadingProdutos] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    setIsLoadingProdutos(true);
    atendimentoService.getProductos()
      .then(response => {
        setProdutos(response.data || []);
        if (response.data && response.data.length > 0) {
          // Opcional: pré-selecionar o primeiro produto
          // setProdutoSelecionadoId(response.data[0].id);
        }
      })
      .catch(err => {
        console.error("Erro ao buscar produtos:", err);
        setError("Não foi possível carregar os produtos.");
      })
      .finally(() => {
        setIsLoadingProdutos(false);
      });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage('');

    if (!produtoSelecionadoId || quantidade <= 0) {
      setError("Por favor, selecione um produto e informe uma quantidade válida.");
      return;
    }

    const itemData = {
      produto_id: parseInt(produtoSelecionadoId),
      quantidade: parseInt(quantidade),
      observacoes_item: observacoes, // O backend espera 'observacoes_item'
    };

    try {
      const response = await atendimentoService.adicionarItemAoPedido(pedidoId, itemData);
      setSuccessMessage(`${response.data.quantidade}x ${response.data.produto?.nome || 'Item'} adicionado com sucesso!`);
      if (onItemAdicionado) {
        onItemAdicionado(response.data); // Callback para atualizar a lista de itens no pai
      }
      // Limpar formulário após sucesso
      setProdutoSelecionadoId('');
      setQuantidade(1);
      setObservacoes('');
      setTimeout(() => setSuccessMessage(''), 3000); // Limpa mensagem de sucesso
    } catch (err) {
      console.error("Erro ao adicionar item:", err);
      setError(err.response?.data?.detail || "Falha ao adicionar item. Verifique o status do pedido.");
    }
  };

  const formStyle = {
    marginTop: '20px',
    padding: '15px',
    border: '1px solid #e0e0e0',
    borderRadius: '5px',
    backgroundColor: '#fcfcfc',
  };

  const inputGroupStyle = {
    marginBottom: '10px',
  };

  const labelStyle = {
    display: 'block',
    marginBottom: '5px',
    fontWeight: 'bold',
  };

  const inputStyle = {
    width: 'calc(100% - 12px)', // Ajustar para padding
    padding: '8px',
    border: '1px solid #ccc',
    borderRadius: '4px',
  };
  
  const buttonStyle = {
    padding: '10px 15px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  };


  if (isLoadingProdutos) {
    return <p>Carregando produtos...</p>;
  }

  return (
    <form onSubmit={handleSubmit} style={formStyle}>
      <h4>Adicionar Item ao Pedido #{pedidoId}</h4>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {successMessage && <p style={{ color: 'green' }}>{successMessage}</p>}
      
      <div style={inputGroupStyle}>
        <label htmlFor="produto" style={labelStyle}>Produto:</label>
        <select
          id="produto"
          value={produtoSelecionadoId}
          onChange={(e) => setProdutoSelecionadoId(e.target.value)}
          required
          style={inputStyle}
        >
          <option value="">Selecione um produto</option>
          {produtos.map((produto) => (
            <option key={produto.id} value={produto.id}>
              {produto.nome} (R$ {parseFloat(produto.preco_base).toFixed(2)})
            </option>
          ))}
        </select>
      </div>

      <div style={inputGroupStyle}>
        <label htmlFor="quantidade" style={labelStyle}>Quantidade:</label>
        <input
          id="quantidade"
          type="number"
          value={quantidade}
          onChange={(e) => setQuantidade(parseInt(e.target.value, 10))}
          min="1"
          required
          style={inputStyle}
        />
      </div>

      <div style={inputGroupStyle}>
        <label htmlFor="observacoes" style={labelStyle}>Observações (opcional):</label>
        <input
          id="observacoes"
          type="text"
          value={observacoes}
          onChange={(e) => setObservacoes(e.target.value)}
          style={inputStyle}
        />
      </div>

      <button type="submit" style={buttonStyle}>Adicionar ao Pedido</button>
    </form>
  );
};

export default AdicionarItemForm;
