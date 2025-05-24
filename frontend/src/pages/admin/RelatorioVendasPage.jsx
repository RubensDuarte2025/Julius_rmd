import React, { useState, useEffect, useCallback } from 'react';
import adminService from '../../services/adminService';
import AdminTable from '../../components/admin/common/AdminTable';

const RelatorioVendasPage = () => {
  const [vendas, setVendas] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dataInicio, setDataInicio] = useState('');
  const [dataFim, setDataFim] = useState('');

  const fetchVendas = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params = {};
      if (dataInicio) params.data_inicio = dataInicio;
      if (dataFim) params.data_fim = dataFim;
      
      const response = await adminService.getRelatorioVendas(params);
      setVendas(response.data || []);
    } catch (err) {
      console.error("Erro ao buscar relatório de vendas:", err);
      setError("Falha ao carregar relatório de vendas.");
      setVendas([]);
    } finally {
      setIsLoading(false);
    }
  }, [dataInicio, dataFim]);

  // Fetch on initial load or when dates change
  // useEffect(() => {
  //   fetchVendas(); // Pode ser chamado aqui ou apenas via botão
  // }, [fetchVendas]); // Removido para carregar apenas ao clicar no botão

  const handleGerarRelatorio = (e) => {
    e.preventDefault();
    if (!dataInicio || !dataFim) {
        alert("Por favor, selecione data de início e data de fim.");
        return;
    }
    fetchVendas();
  };

  const columns = [
    { header: 'ID Pag.', key: 'id_pagamento' },
    { header: 'ID Pedido', key: 'id_pedido_origem' },
    { header: 'Origem', key: 'origem_pedido' },
    { header: 'Data Pag.', key: 'data_pagamento', render: (row) => new Date(row.data_pagamento).toLocaleString() },
    { header: 'Valor Pago', key: 'valor_pago', render: (row) => `R$ ${parseFloat(row.valor_pago).toFixed(2)}` },
    { header: 'Método', key: 'metodo_pagamento' },
  ];
  
  const pageStyle = { padding: '20px' };
  const formStyle = { display: 'flex', gap: '10px', marginBottom: '20px', alignItems: 'center' };
  const inputStyle = { padding: '8px', border: '1px solid #ccc', borderRadius: '4px' };
  const buttonStyle = { padding: '8px 15px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' };

  return (
    <div style={pageStyle}>
      <h2>Relatório de Vendas Simples</h2>
      <form onSubmit={handleGerarRelatorio} style={formStyle}>
        <div>
          <label htmlFor="dataInicio" style={{marginRight: '5px'}}>Data Início:</label>
          <input 
            type="date" 
            id="dataInicio" 
            value={dataInicio} 
            onChange={(e) => setDataInicio(e.target.value)} 
            required
            style={inputStyle} 
          />
        </div>
        <div>
          <label htmlFor="dataFim" style={{marginRight: '5px'}}>Data Fim:</label>
          <input 
            type="date" 
            id="dataFim" 
            value={dataFim} 
            onChange={(e) => setDataFim(e.target.value)} 
            required
            style={inputStyle} 
          />
        </div>
        <button type="submit" disabled={isLoading} style={buttonStyle}>
          {isLoading ? 'Gerando...' : 'Gerar Relatório'}
        </button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}
      
      <AdminTable columns={columns} data={vendas} />
      
      {vendas.length > 0 && (
        <div style={{marginTop: '20px', fontWeight: 'bold'}}>
            Total de Vendas no Período: R$ {
                vendas.reduce((acc, venda) => acc + parseFloat(venda.valor_pago), 0).toFixed(2)
            }
        </div>
      )}
    </div>
  );
};

export default RelatorioVendasPage;
