import React, { useState, useEffect, useCallback } from 'react';
import adminService from '../../services/adminService';
import AdminTable from '../../components/admin/common/AdminTable';

const RelatorioProdutosPage = () => {
  const [produtosVendidos, setProdutosVendidos] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dataInicio, setDataInicio] = useState('');
  const [dataFim, setDataFim] = useState('');

  const fetchProdutosVendidos = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params = {};
      if (dataInicio) params.data_inicio = dataInicio;
      if (dataFim) params.data_fim = dataFim;
      
      const response = await adminService.getRelatorioProdutosVendidos(params);
      setProdutosVendidos(response.data || []);
    } catch (err) {
      console.error("Erro ao buscar relatório de produtos vendidos:", err);
      setError("Falha ao carregar relatório de produtos vendidos.");
      setProdutosVendidos([]);
    } finally {
      setIsLoading(false);
    }
  }, [dataInicio, dataFim]);

  const handleGerarRelatorio = (e) => {
    e.preventDefault();
    if (!dataInicio || !dataFim) {
        alert("Por favor, selecione data de início e data de fim.");
        return;
    }
    fetchProdutosVendidos();
  };

  const columns = [
    { header: 'Nome do Produto', key: 'nome_produto' },
    { header: 'Quantidade Vendida', key: 'quantidade_total_vendida' },
  ];
  
  const pageStyle = { padding: '20px' };
  const formStyle = { display: 'flex', gap: '10px', marginBottom: '20px', alignItems: 'center' };
  const inputStyle = { padding: '8px', border: '1px solid #ccc', borderRadius: '4px' };
  const buttonStyle = { padding: '8px 15px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' };

  return (
    <div style={pageStyle}>
      <h2>Relatório de Produtos Vendidos</h2>
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
      
      <AdminTable columns={columns} data={produtosVendidos} />
    </div>
  );
};

export default RelatorioProdutosPage;
