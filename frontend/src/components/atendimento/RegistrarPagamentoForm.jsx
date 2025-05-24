import React, { useState } from 'react';
// As opções de método de pagamento virão do modelo Pagamento, que foi usado no serializer PagamentoRegistroSerializer
// em atendimento_interno.serializers.py.
// MANUAL_PAYMENT_METHODS de lá:
// (PagamentoModel.METODO_DINHEIRO, 'Dinheiro'),
// (PagamentoModel.METODO_CARTAO_DEBITO_MAQUINETA, 'Cartão de Débito (Maquineta)'),
// (PagamentoModel.METODO_CARTAO_CREDITO_MAQUINETA, 'Cartão de Crédito (Maquineta)'),
// (PagamentoModel.METODO_PIX, 'PIX (Maquineta/QR Fixo)'),
// (PagamentoModel.METODO_OUTRO, 'Outro'),

const METODOS_PAGAMENTO_MANUAL = [
  { valor: 'dinheiro', label: 'Dinheiro' },
  { valor: 'cartao_debito_maquineta', label: 'Cartão de Débito (Maquineta)' },
  { valor: 'cartao_credito_maquineta', label: 'Cartão de Crédito (Maquineta)' },
  { valor: 'pix', label: 'PIX (Maquineta/QR Fixo)' }, // No modelo Pagamento é 'pix', serializer do atendimento usa 'pix_maquineta'
  { valor: 'outro', label: 'Outro' },
];
// Nota: O serializer PagamentoRegistroSerializer em atendimento_interno.serializers.py foi atualizado para usar
// MANUAL_PAYMENT_METHODS, que inclui 'pix' como chave.
// Então, o valor 'pix' aqui é compatível.

const RegistrarPagamentoForm = ({ pedido, onPagamentoSubmit, onCancel }) => {
  const [metodoPagamento, setMetodoPagamento] = useState(METODOS_PAGAMENTO_MANUAL[0].valor); // Default para Dinheiro
  // O valor total do pedido é uma boa sugestão para o valor pago.
  const valorSugerido = pedido && pedido.total_pedido ? parseFloat(pedido.total_pedido).toFixed(2) : '0.00';
  const [valorPago, setValorPago] = useState(valorSugerido);
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Atualiza valorPago se o valorSugerido mudar (ex: pedido atualizado)
  React.useEffect(() => {
    setValorPago(valorSugerido);
  }, [valorSugerido]);


  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    if (parseFloat(valorPago) <= 0) {
      setError("O valor pago deve ser maior que zero.");
      setIsSubmitting(false);
      return;
    }
    if (!metodoPagamento) {
        setError("Por favor, selecione um método de pagamento.");
        setIsSubmitting(false);
        return;
    }

    const pagamentoData = {
      metodo: metodoPagamento,
      valor_pago: parseFloat(valorPago),
    };

    try {
      await onPagamentoSubmit(pagamentoData);
      // O componente pai (ex: Modal ou Página) fechará o form/modal e lidará com o redirecionamento.
    } catch (err) {
      console.error("Erro no formulário de pagamento:", err);
      setError(err.response?.data?.detail || "Falha ao registrar pagamento.");
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const formStyle = {
    padding: '20px',
    border: '1px solid #ccc',
    borderRadius: '8px',
    backgroundColor: 'white',
    boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
  };

  const inputGroupStyle = {
    marginBottom: '15px',
  };

  const labelStyle = {
    display: 'block',
    marginBottom: '5px',
    fontWeight: '500',
  };

  const inputStyle = {
    width: 'calc(100% - 16px)',
    padding: '8px',
    border: '1px solid #ccc',
    borderRadius: '4px',
  };
  
  const buttonContainerStyle = {
    marginTop: '20px',
    display: 'flex',
    justifyContent: 'space-between',
  };

  const buttonStyle = {
    padding: '10px 15px',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: 'bold',
  };

  const submitButtonStyle = {
    ...buttonStyle,
    backgroundColor: '#28a745',
    color: 'white',
  };

  const cancelButtonStyle = {
    ...buttonStyle,
    backgroundColor: '#6c757d',
    color: 'white',
  };


  return (
    <form onSubmit={handleSubmit} style={formStyle}>
      <h3>Registrar Pagamento para Pedido #{pedido?.id}</h3>
      <p>Total do Pedido: R$ {valorSugerido}</p>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      
      <div style={inputGroupStyle}>
        <label htmlFor="metodoPagamento" style={labelStyle}>Método de Pagamento:</label>
        <select
          id="metodoPagamento"
          value={metodoPagamento}
          onChange={(e) => setMetodoPagamento(e.target.value)}
          required
          style={inputStyle}
        >
          {METODOS_PAGAMENTO_MANUAL.map(metodo => (
            <option key={metodo.valor} value={metodo.valor}>
              {metodo.label}
            </option>
          ))}
        </select>
      </div>

      <div style={inputGroupStyle}>
        <label htmlFor="valorPago" style={labelStyle}>Valor Pago:</label>
        <input
          id="valorPago"
          type="number"
          value={valorPago}
          onChange={(e) => setValorPago(e.target.value)}
          min="0.01"
          step="0.01"
          required
          style={inputStyle}
        />
      </div>
      
      <div style={buttonContainerStyle}>
        {onCancel && (
            <button type="button" onClick={onCancel} style={cancelButtonStyle} disabled={isSubmitting}>
                Cancelar
            </button>
        )}
        <button type="submit" style={submitButtonStyle} disabled={isSubmitting}>
          {isSubmitting ? 'Registrando...' : 'Confirmar Pagamento'}
        </button>
      </div>
    </form>
  );
};

export default RegistrarPagamentoForm;
