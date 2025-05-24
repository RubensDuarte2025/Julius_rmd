import React, { useState, useEffect, useCallback } from 'react';
import adminService from '../../services/adminService';
import AdminTable from '../../components/admin/common/AdminTable';
import Modal from '../../components/common/Modal'; // Re-using common modal

// Simple form for editing a configuration value
const ConfiguracaoEditForm = ({ config, onSubmit, onCancel }) => {
  const [valor, setValor] = useState(config.valor);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(config.chave, { valor });
  };

  return (
    <form onSubmit={handleSubmit} style={{ padding: '10px' }}>
      <h4>Editar Configuração: {config.chave}</h4>
      <p><small>{config.descricao}</small></p>
      <div style={{ marginBottom: '15px' }}>
        <label htmlFor="valor" style={{ display: 'block', marginBottom: '5px' }}>Valor:</label>
        <textarea
          id="valor"
          value={valor}
          onChange={(e) => setValor(e.target.value)}
          rows={3}
          style={{ width: '100%', padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
        />
      </div>
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
        <button type="button" onClick={onCancel} style={{ padding: '8px 12px', borderRadius: '4px', border: '1px solid #6c757d', backgroundColor: '#6c757d', color: 'white' }}>
          Cancelar
        </button>
        <button type="submit" style={{ padding: '8px 12px', borderRadius: '4px', border: 'none', backgroundColor: '#007bff', color: 'white' }}>
          Salvar Alterações
        </button>
      </div>
    </form>
  );
};


const GerenciarConfiguracoesPage = () => {
  const [configuracoes, setConfiguracoes] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [configAtual, setConfigAtual] = useState(null);

  const fetchConfiguracoes = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await adminService.getConfiguracoes();
      setConfiguracoes(response.data || []);
    } catch (err) {
      console.error("Erro ao buscar configurações:", err);
      setError("Falha ao carregar configurações.");
      setConfiguracoes([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchConfiguracoes();
  }, [fetchConfiguracoes]);

  const handleOpenEditModal = (config) => {
    setConfigAtual(config);
    setShowEditModal(true);
  };

  const handleCloseEditModal = () => {
    setConfigAtual(null);
    setShowEditModal(false);
  };

  const handleUpdateConfig = async (chave, data) => {
    try {
      await adminService.updateConfiguracao(chave, data);
      fetchConfiguracoes(); // Re-fetch
      handleCloseEditModal();
    } catch (err) {
      console.error("Erro ao atualizar configuração:", err);
      // Idealmente, mostrar erro no modal ou na página
      alert("Erro ao atualizar: " + (err.response?.data?.detail || err.message));
    }
  };

  const columns = [
    { header: 'Chave', key: 'chave', render: (row) => <strong>{row.chave}</strong> },
    { header: 'Valor', key: 'valor', render: (row) => <pre style={{whiteSpace: 'pre-wrap', wordBreak: 'break-all', margin: 0}}>{String(row.valor)}</pre> },
    { header: 'Descrição', key: 'descricao' },
  ];
  
  const pageStyle = { padding: '20px' };

  if (isLoading) {
    return <p style={pageStyle}>Carregando configurações...</p>;
  }

  if (error) {
    return <p style={{...pageStyle, color: 'red' }}>{error}</p>;
  }

  return (
    <div style={pageStyle}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Gerenciar Configurações do Sistema</h2>
        {/* Botão para adicionar nova config pode ser Pós-MVP, pois chaves são geralmente predefinidas */}
      </div>
      
      <AdminTable 
        columns={columns} 
        data={configuracoes} 
        onEdit={handleOpenEditModal} 
        // onDelete não é comum para configurações, a menos que sejam dinâmicas.
      />

      {showEditModal && configAtual && (
        <Modal isOpen={showEditModal} onClose={handleCloseEditModal} title={`Editar Configuração: ${configAtual.chave}`}>
          <ConfiguracaoEditForm
            config={configAtual}
            onSubmit={handleUpdateConfig}
            onCancel={handleCloseEditModal}
          />
        </Modal>
      )}
    </div>
  );
};

export default GerenciarConfiguracoesPage;
