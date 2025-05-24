import React, { useState, useEffect, useCallback } from 'react';
import adminService from '../../services/adminService';
import AdminTable from '../../components/admin/common/AdminTable';
import Modal from '../../components/common/Modal';

// Simple form for Categoria
const CategoriaForm = ({ categoria, onSubmit, onCancel }) => {
  const [nome, setNome] = useState(categoria?.nome || '');
  const [descricao, setDescricao] = useState(categoria?.descricao || '');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!nome) {
      setError('Nome da categoria é obrigatório.');
      return;
    }
    const categoriaData = { nome, descricao };
    try {
      await onSubmit(categoriaData);
    } catch (err) {
      setError(err.response?.data?.detail || err.response?.data?.nome?.[0] || err.message || "Erro ao salvar categoria.");
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
        <label htmlFor="nomeCategoria" style={labelStyle}>Nome:</label>
        <input
          type="text"
          id="nomeCategoria"
          value={nome}
          onChange={(e) => setNome(e.target.value)}
          required
          style={inputStyle}
        />
      </div>
      <div style={inputGroupStyle}>
        <label htmlFor="descricaoCategoria" style={labelStyle}>Descrição (opcional):</label>
        <textarea
          id="descricaoCategoria"
          value={descricao}
          onChange={(e) => setDescricao(e.target.value)}
          rows={3}
          style={inputStyle}
        />
      </div>
      <div style={buttonContainerStyle}>
        <button type="button" onClick={onCancel} style={{ padding: '8px 12px', borderRadius: '4px', border: '1px solid #6c757d', backgroundColor: '#6c757d', color: 'white' }}>
          Cancelar
        </button>
        <button type="submit" style={{ padding: '8px 12px', borderRadius: '4px', border: 'none', backgroundColor: '#007bff', color: 'white' }}>
          {categoria ? 'Atualizar Categoria' : 'Criar Categoria'}
        </button>
      </div>
    </form>
  );
};


const GerenciarCategoriasPage = () => {
  const [categorias, setCategorias] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showFormModal, setShowFormModal] = useState(false);
  const [categoriaAtual, setCategoriaAtual] = useState(null); // Para edição

  const fetchCategorias = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await adminService.getCategorias();
      setCategorias(response.data || []);
    } catch (err) {
      console.error("Erro ao buscar categorias:", err);
      setError("Falha ao carregar categorias.");
      setCategorias([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCategorias();
  }, [fetchCategorias]);

  const handleOpenFormModal = (categoria = null) => {
    setCategoriaAtual(categoria);
    setShowFormModal(true);
  };

  const handleCloseFormModal = () => {
    setCategoriaAtual(null);
    setShowFormModal(false);
  };

  const handleSubmitCategoriaForm = async (categoriaData) => {
    // O try-catch está dentro do CategoriaForm para feedback de erro mais próximo.
    if (categoriaAtual) {
      await adminService.updateCategoria(categoriaAtual.id, categoriaData);
    } else {
      await adminService.createCategoria(categoriaData);
    }
    fetchCategorias(); // Re-fetch
    handleCloseFormModal();
  };

  const handleDeleteCategoria = async (categoriaId) => {
    if (window.confirm(`Tem certeza que deseja excluir a categoria ID ${categoriaId}? Isso pode falhar se houver produtos associados.`)) {
      try {
        await adminService.deleteCategoria(categoriaId);
        fetchCategorias(); // Re-fetch
      } catch (err) {
        console.error("Erro ao excluir categoria:", err);
        alert("Erro ao excluir categoria: " + (err.response?.data?.detail || err.message));
      }
    }
  };

  const columns = [
    { header: 'ID', key: 'id' },
    { header: 'Nome', key: 'nome' },
    { header: 'Descrição', key: 'descricao' },
  ];
  
  const pageStyle = { padding: '20px' };
  const buttonStyle = { padding: '10px 15px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', marginBottom: '20px' };

  if (isLoading) return <p style={pageStyle}>Carregando categorias...</p>;
  if (error) return <p style={{...pageStyle, color: 'red' }}>{error}</p>;

  return (
    <div style={pageStyle}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <h2>Gerenciar Categorias de Produtos</h2>
        <button onClick={() => handleOpenFormModal()} style={buttonStyle}>
          Nova Categoria
        </button>
      </div>
      
      <AdminTable 
        columns={columns} 
        data={categorias} 
        onEdit={handleOpenFormModal}
        onDelete={handleDeleteCategoria}
      />

      {showFormModal && (
        <Modal isOpen={showFormModal} onClose={handleCloseFormModal} title={categoriaAtual ? 'Editar Categoria' : 'Nova Categoria'}>
          <CategoriaForm
            categoria={categoriaAtual}
            onSubmit={handleSubmitCategoriaForm}
            onCancel={handleCloseFormModal}
          />
        </Modal>
      )}
    </div>
  );
};

export default GerenciarCategoriasPage;
