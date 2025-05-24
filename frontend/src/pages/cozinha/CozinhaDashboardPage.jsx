import React, { useState, useEffect, useCallback } from 'react';
import cozinhaService from '../../services/cozinhaService';
import PedidoCozinhaCard from '../../components/cozinha/PedidoCozinhaCard';

const CozinhaDashboardPage = () => {
  const [pedidos, setPedidos] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchPedidos = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await cozinhaService.getPedidosParaPreparar();
      // A API retorna os pedidos já ordenados por horario_entrada_cozinha
      setPedidos(response.data || []); 
    } catch (err) {
      setError("Erro ao buscar pedidos. Tente atualizar.");
      console.error("Erro detalhado:", err.response?.data || err.message);
      setPedidos([]); // Limpa pedidos em caso de erro
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPedidos();
    // Opcional: configurar um intervalo para auto-atualização (Pós-MVP)
    // const intervalId = setInterval(fetchPedidos, 30000); // Atualiza a cada 30 segundos
    // return () => clearInterval(intervalId);
  }, [fetchPedidos]);

  const handlePedidoStatusAtualizado = useCallback((_pedidoIdOrigem, _tipoOrigem, novoStatus) => {
    // Quando um pedido é marcado como "Pronto", ele não aparecerá mais na lista
    // de "pedidos_para_preparar" na próxima busca.
    // Se o status mudou para "Em Preparo", o card mudará de cor/estilo, mas permanece.
    // Para MVP, re-fetch é a maneira mais simples de garantir que a lista está atualizada.
    // A API `getPedidosParaPreparar` já filtra por 'AguardandoPreparo' ou 'EmPreparo'.
    // Então, se um pedido vai para 'Pronto', ele naturalmente some da lista ao re-buscar.
    fetchPedidos();
  }, [fetchPedidos]);

  // Estilos
  const pageStyle = {
    padding: '20px',
    fontFamily: '"Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  };

  const headerStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
  };

  const titleStyle = {
    margin: 0,
    color: '#333',
  };

  const buttonStyle = {
    padding: '10px 15px',
    fontSize: '1em',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  };
  
  const pedidosContainerStyle = {
    display: 'flex',
    flexWrap: 'wrap', // Permite que os cards quebrem para a próxima linha
    gap: '20px', // Espaçamento entre os cards
    justifyContent: 'flex-start', // Alinha cards à esquerda
  };

  const messageStyle = {
    textAlign: 'center',
    fontSize: '1.1em',
    color: '#555',
    marginTop: '30px',
  };

  if (isLoading && pedidos.length === 0) {
    return <p style={messageStyle}>Carregando pedidos da cozinha...</p>;
  }

  if (error) {
    return (
      <div style={pageStyle}>
        <div style={headerStyle}>
            <h1 style={titleStyle}>Painel da Cozinha</h1>
            <button onClick={fetchPedidos} disabled={isLoading} style={buttonStyle}>
                {isLoading ? 'Atualizando...' : 'Tentar Novamente'}
            </button>
        </div>
        <p style={{ ...messageStyle, color: 'red' }}>{error}</p>
      </div>
    );
  }

  return (
    <div style={pageStyle}>
      <div style={headerStyle}>
        <h1 style={titleStyle}>Painel da Cozinha</h1>
        <button onClick={fetchPedidos} disabled={isLoading} style={buttonStyle}>
          {isLoading ? 'Atualizando...' : 'Atualizar Lista'}
        </button>
      </div>

      {pedidos.length === 0 && !isLoading && (
        <p style={messageStyle}>Nenhum pedido para preparar no momento.</p>
      )}

      <div style={pedidosContainerStyle}>
        {pedidos.map(pedido => (
          <PedidoCozinhaCard
            key={`${pedido.tipo_origem}-${pedido.id_pedido_origem}`}
            pedido={pedido}
            onAtualizarStatus={handlePedidoStatusAtualizado}
          />
        ))}
      </div>
    </div>
  );
};

export default CozinhaDashboardPage;
