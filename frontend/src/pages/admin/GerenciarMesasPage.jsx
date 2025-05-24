import React, { useState, useEffect, useCallback } from 'react';
import adminService from '../../services/adminService';
import AdminTable from '../../components/admin/common/AdminTable';
import Modal from '../../components/common/Modal';

// Simple form for Mesa
const MesaForm = ({ mesa, onSubmit, onCancel }) => {
  const [numeroIdentificador, setNumeroIdentificador] = useState(mesa?.numero_identificador || '');
  const [capacidadeDefault, setCapacidadeDefault] = useState(mesa?.capacidade_default || 4);
  // Status é gerenciado operacionalmente, mas pode ser definido na criação ou por admin em casos especiais
  const [status, setStatus] = useState(mesa?.status || 'Livre'); 
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!numeroIdentificador) {
      setError('Número/Identificador é obrigatório.');
      return;
    }
    const mesaData = { 
        numero_identificador: numeroIdentificador, 
        capacidade_default: parseInt(capacidadeDefault, 10),
        status // Incluindo status, embora o backend de admin possa ou não permitir alterá-lo diretamente aqui
    };
    try {
      await onSubmit(mesaData);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Erro ao salvar mesa.");
    }
  };
  
  const formStyle = { padding: '10px' };
  const inputGroupStyle = { marginBottom: '15px' };
  const labelStyle = { display: 'block', marginBottom: '5px', fontWeight: 'bold' };
  const inputStyle = { width: '100%', padding: '8px', border: '1px solid #ccc', borderRadius: '4px', boxSizing: 'border-box' };
  const buttonContainerStyle = { display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '20px' };


  return (
    <form onSubmit={handleSubmit} style={formStyle}>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <div style={inputGroupStyle}>
        <label htmlFor="numeroIdentificador" style={labelStyle}>Número/Identificador:</label>
        <input
          type="text"
          id="numeroIdentificador"
          value={numeroIdentificador}
          onChange={(e) => setNumeroIdentificador(e.target.value)}
          required
          style={inputStyle}
        />
      </div>
      <div style={inputGroupStyle}>
        <label htmlFor="capacidadeDefault" style={labelStyle}>Capacidade Padrão:</label>
        <input
          type="number"
          id="capacidadeDefault"
          value={capacidadeDefault}
          onChange={(e) => setCapacidadeDefault(e.target.value)}
          min="1"
          required
          style={inputStyle}
        />
      </div>
       <div style={inputGroupStyle}>
        <label htmlFor="statusMesa" style={labelStyle}>Status (Admin):</label>
        <select 
            id="statusMesa" 
            value={status} 
            onChange={(e) => setStatus(e.target.value)} 
            style={inputStyle}
        >
            {/* Estas são as opções do modelo Mesa */}
            <option value="Livre">Livre</option>
            <option value="Ocupada">Ocupada (Operacional)</option>
            <option value="AguardandoPagamento">Aguardando Pagamento (Operacional)</option>
            <option value="Interditada">Interditada</option>
        </select>
        <small>Nota: Status 'Ocupada' e 'AguardandoPagamento' são geralmente controlados operacionalmente.</small>
      </div>
      <div style={buttonContainerStyle}>
        <button type="button" onClick={onCancel} style={{ padding: '8px 12px', borderRadius: '4px', border: '1px solid #6c757d', backgroundColor: '#6c757d', color: 'white' }}>
          Cancelar
        </button>
        <button type="submit" style={{ padding: '8px 12px', borderRadius: '4px', border: 'none', backgroundColor: '#007bff', color: 'white' }}>
          {mesa ? 'Atualizar Mesa' : 'Criar Mesa'}
        </button>
      </div>
    </form>
  );
};


const GerenciarMesasPage = () => {
  const [mesas, setMesas] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showFormModal, setShowFormModal] = useState(false);
  const [mesaAtual, setMesaAtual] = useState(null); // Para edição

  const fetchMesas = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await adminService.getMesas();
      setMesas(response.data || []);
    } catch (err) {
      console.error("Erro ao buscar mesas:", err);
      setError("Falha ao carregar mesas.");
      setMesas([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMesas();
  }, [fetchMesas]);

  const handleOpenFormModal = (mesa = null) => {
    setMesaAtual(mesa);
    setShowFormModal(true);
  };

  const handleCloseFormModal = () => {
    setMesaAtual(null);
    setShowFormModal(false);
  };

  const handleSubmitMesaForm = async (mesaData) => {
    // O try-catch está dentro do MesaForm para feedback de erro mais próximo.
    // Se o submit no MesaForm for bem-sucedido, ele chama este onSubmit.
    if (mesaAtual) {
      await adminService.updateMesa(mesaAtual.id, mesaData);
    } else {
      await adminService.createMesa(mesaData);
    }
    fetchMesas(); // Re-fetch
    handleCloseFormModal();
  };

  const handleDeleteMesa = async (mesaId) => {
    if (window.confirm(`Tem certeza que deseja excluir a mesa ID ${mesaId}? Isso pode falhar se houver pedidos associados.`)) {
      try {
        await adminService.deleteMesa(mesaId);
        fetchMesas(); // Re-fetch
      } catch (err) {
        console.error("Erro ao excluir mesa:", err);
        alert("Erro ao excluir mesa: " + (err.response?.data?.detail || err.message));
      }
    }
  };

  const columns = [
    { header: 'ID', key: 'id' },
    { header: 'Número/Identificador', key: 'numero_identificador' },
    { header: 'Capacidade', key: 'capacidade_default' },
    { header: 'Status (Operacional)', key: 'status' },
  ];
  
  const pageStyle = { padding: '20px' };
  const buttonStyle = { padding: '10px 15px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', marginBottom: '20px' };


  if (isLoading) return <p style={pageStyle}>Carregando mesas...</p>;
  if (error) return <p style={{...pageStyle, color: 'red' }}>{error}</p>;

  return (
    <div style={pageStyle}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <h2>Gerenciar Mesas</h2>
        <button onClick={() => handleOpenFormModal()} style={buttonStyle}>
          Nova Mesa
        </button>
      </div>
      
      <AdminTable 
        columns={columns} 
        data={mesas} 
        onEdit={handleOpenFormModal}
        onDelete={handleDeleteMesa}
      />

      {showFormModal && (
        <Modal isOpen={showFormModal} onClose={handleCloseFormModal} title={mesaAtual ? 'Editar Mesa' : 'Nova Mesa'}>
          <MesaForm
            mesa={mesaAtual}
            onSubmit={handleSubmitMesaForm}
            onCancel={handleCloseFormModal}
          />
        </Modal>
      )}
    </div>
  );
};

export default GerenciarMesasPage;
