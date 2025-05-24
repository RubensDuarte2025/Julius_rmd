import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import atendimentoService from '../../services/atendimentoService';
import DetalhesPedidoMesa from '../../components/atendimento/DetalhesPedidoMesa';
import AdicionarItemForm from '../../components/atendimento/AdicionarItemForm';
import RegistrarPagamentoForm from '../../components/atendimento/RegistrarPagamentoForm';
import Modal from '../../components/common/Modal'; // Assuming Modal is in common

const PedidoMesaOperacaoPage = () => {
  const { mesaId } = useParams();
  const navigate = useNavigate();

  const [mesa, setMesa] = useState(null); // Para armazenar detalhes da mesa, se necessário
  const [pedido, setPedido] = useState(null); // O pedido ativo ou a ser criado
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showPagamentoModal, setShowPagamentoModal] = useState(false);

  // Função para carregar ou criar o pedido para a mesa
  const carregarOuCriarPedido = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Tenta obter/criar um pedido ativo para a mesa.
      // O backend em /api/mesas/{mesaId}/pedidos/ foi projetado para:
      // - Criar um novo pedido se a mesa estiver livre ou se o último pedido estiver pago/cancelado.
      // - Retornar o pedido 'Aberto' ou 'Fechado' (aguardando pagamento) existente.
      const response = await atendimentoService.getOrCreateActivePedidoForMesa(mesaId);
      setPedido(response.data);
      // Opcional: carregar detalhes da mesa se necessário para exibição
      // const mesaResponse = await atendimentoService.getMesaDetalhes(mesaId);
      // setMesa(mesaResponse.data);
    } catch (err) {
      console.error("Erro ao carregar ou criar pedido:", err);
      setError(err.response?.data?.detail || "Falha ao carregar dados do pedido. A mesa pode estar indisponível ou já ter um pedido que não pode ser modificado.");
      // Se houver erro (ex: mesa interditada, ou já tem pedido e a API não retorna),
      // o usuário pode precisar ser redirecionado ou ver uma mensagem específica.
    } finally {
      setIsLoading(false);
    }
  }, [mesaId]);

  useEffect(() => {
    carregarOuCriarPedido();
  }, [carregarOuCriarPedido]);

  const handleItemAdicionado = () => {
    // Após adicionar um item, recarrega os dados do pedido para refletir a mudança
    // (incluindo o total atualizado e o novo item na lista)
    if (pedido && pedido.id) {
      setIsLoading(true); // Mostrar feedback de carregamento
      atendimentoService.getPedidoMesaDetalhes(pedido.id)
        .then(response => setPedido(response.data))
        .catch(err => {
          console.error("Erro ao recarregar pedido após adicionar item:", err);
          setError("Erro ao atualizar detalhes do pedido.");
        })
        .finally(() => setIsLoading(false));
    }
  };

  const handleRemoverItem = async (itemId) => {
    if (!pedido || !itemId) return;
    const confirmar = window.confirm("Tem certeza que deseja remover este item do pedido?");
    if (!confirmar) return;

    try {
      await atendimentoService.removerItemDoPedido(pedido.id, itemId);
      // Recarregar pedido para atualizar a lista e totais
      handleItemAdicionado(); // Reusa a lógica de recarregar
    } catch (err) {
      console.error("Erro ao remover item:", err);
      setError(err.response?.data?.detail || "Falha ao remover item.");
    }
  };
  
  const handleFecharConta = async () => {
    if (!pedido || pedido.status_pedido !== 'Aberto') {
        alert("O pedido precisa estar 'Aberto' para ser fechado para pagamento.");
        return;
    }
    const confirmar = window.confirm("Deseja fechar a conta para pagamento? Não será possível adicionar mais itens após isso.");
    if (!confirmar) return;

    try {
        const updatedPedido = await atendimentoService.atualizarStatusPedidoMesa(pedido.id, { status_pedido: 'Fechado' });
        setPedido(updatedPedido.data);
        setShowPagamentoModal(true); // Abrir modal de pagamento após fechar a conta
    } catch (err) {
        console.error("Erro ao fechar a conta:", err);
        setError(err.response?.data?.detail || "Falha ao fechar a conta.");
    }
  };


  const handleRegistrarPagamento = async (pagamentoData) => {
    if (!pedido) return;
    setError(null); // Limpa erros anteriores
    try {
      await atendimentoService.registrarPagamentoPedido(pedido.id, pagamentoData);
      setShowPagamentoModal(false);
      alert("Pagamento registrado com sucesso! A mesa será liberada.");
      navigate('/atendimento/mesas'); // Redireciona para a lista de mesas
    } catch (err) {
      console.error("Erro ao registrar pagamento:", err);
      // O erro específico do backend (ex: valor incorreto) pode vir em err.response.data.detail
      setError(err.response?.data?.detail || "Falha ao registrar pagamento.");
      // Não fechar o modal automaticamente em caso de erro, para o usuário ver a mensagem.
      // Se for um erro no form, o RegistrarPagamentoForm já deve tratar.
      // Se for um erro da API, mostramos aqui.
      throw err; // Re-throw para que o RegistrarPagamentoForm possa tratar o isSubmitting
    }
  };

  const pageStyle = { padding: '20px', maxWidth: '800px', margin: '0 auto' };
  const headerStyle = { borderBottom: '1px solid #eee', paddingBottom: '10px', marginBottom: '20px' };
  const actionsStyle = { marginTop: '20px', display: 'flex', gap: '10px', flexWrap: 'wrap' };
  const buttonStyle = { padding: '10px 15px', border: 'none', borderRadius: '5px', cursor: 'pointer' };


  if (isLoading && !pedido) { // Mostrar carregando apenas se ainda não tem dados do pedido
    return <p style={{ textAlign: 'center', padding: '20px' }}>Carregando dados da mesa e pedido...</p>;
  }

  if (error) {
    return (
      <div style={pageStyle}>
        <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>
        <button onClick={() => navigate('/atendimento/mesas')} style={{ ...buttonStyle, backgroundColor: '#007bff', color: 'white' }}>
          Voltar para Mesas
        </button>
      </div>
    );
  }

  if (!pedido) {
    // Isso pode acontecer se a API getOrCreateActivePedidoForMesa não retornar um pedido
    // (ex: mesa não existe ou erro inesperado não capturado acima)
    return (
        <div style={pageStyle}>
            <p style={{ textAlign: 'center' }}>Não foi possível carregar ou criar um pedido para esta mesa.</p>
            <button onClick={() => navigate('/atendimento/mesas')} style={{ ...buttonStyle, backgroundColor: '#007bff', color: 'white' }}>
                Voltar para Mesas
            </button>
        </div>
    );
  }
  
  const podeAdicionarItens = pedido.status_pedido === 'Aberto';
  const podeFecharConta = pedido.status_pedido === 'Aberto' && pedido.itens_pedido && pedido.itens_pedido.length > 0;
  const podeRegistrarPagamento = pedido.status_pedido === 'Fechado';


  return (
    <div style={pageStyle}>
      <header style={headerStyle}>
        {/* Idealmente, teríamos o número da mesa aqui. Se `mesa` for carregado: `Mesa ${mesa?.numero_identificador}` */}
        <h2>Operação da Mesa {mesaId} - Pedido #{pedido.id}</h2>
      </header>

      <DetalhesPedidoMesa pedido={pedido} onRemoverItem={podeAdicionarItens ? handleRemoverItem : null} />

      {podeAdicionarItens && (
        <AdicionarItemForm
          pedidoId={pedido.id}
          onItemAdicionado={handleItemAdicionado}
        />
      )}
      {!podeAdicionarItens && pedido.status_pedido !== 'Aberto' && (
        <p style={{ fontStyle: 'italic', marginTop: '20px' }}>
            Não é possível adicionar mais itens a um pedido com status "{pedido.status_pedido}".
        </p>
      )}


      <div style={actionsStyle}>
        {podeFecharConta && (
          <button onClick={handleFecharConta} style={{...buttonStyle, backgroundColor: '#ffc107'}}>
            Fechar Conta
          </button>
        )}
        {podeRegistrarPagamento && (
          <button onClick={() => setShowPagamentoModal(true)} style={{...buttonStyle, backgroundColor: '#28a745', color: 'white'}}>
            Registrar Pagamento
          </button>
        )}
         <button onClick={() => navigate('/atendimento/mesas')} style={{...buttonStyle, backgroundColor: '#6c757d', color: 'white'}}>
            Voltar para Dashboard de Mesas
        </button>
      </div>

      {showPagamentoModal && (
        <Modal isOpen={showPagamentoModal} onClose={() => setShowPagamentoModal(false)} title="Registrar Pagamento">
          <RegistrarPagamentoForm
            pedido={pedido}
            onPagamentoSubmit={handleRegistrarPagamento}
            onCancel={() => setShowPagamentoModal(false)}
          />
        </Modal>
      )}
    </div>
  );
};

export default PedidoMesaOperacaoPage;
