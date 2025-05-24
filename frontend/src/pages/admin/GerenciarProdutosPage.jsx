import React, { useState, useEffect, useCallback } from 'react';
import adminService from '../../services/adminService';
import AdminTable from '../../components/admin/common/AdminTable';
import Modal from '../../components/common/Modal';

// Simple form for Produto
const ProdutoForm = ({ produto, categorias, onSubmit, onCancel }) => {
  const [nome, setNome] = useState(produto?.nome || '');
  const [descricao, setDescricao] = useState(produto?.descricao || '');
  const [precoBase, setPrecoBase] = useState(produto?.preco_base || '');
  const [categoriaId, setCategoriaId] = useState(produto?.categoria_id || produto?.categoria?.id || '');
  const [disponivel, setDisponivel] = useState(produto ? produto.disponivel : true);
  const [ingredientesBase, setIngredientesBase] = useState(produto?.ingredientes_base || '');
  const [fotoUrl, setFotoUrl] = useState(produto?.foto_url || '');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!nome || !precoBase || !categoriaId) {
      setError('Nome, Preço Base e Categoria são obrigatórios.');
      return;
    }
    const produtoData = {
      nome,
      descricao,
      preco_base: parseFloat(precoBase),
      categoria_id: parseInt(categoriaId),
      disponivel,
      ingredientes_base: ingredientesBase,
      foto_url: fotoUrl,
    };
    try {
      await onSubmit(produtoData);
    } catch (err) {
      setError(err.response?.data?.detail || JSON.stringify(err.response?.data) || err.message || "Erro ao salvar produto.");
    }
  };

  const formStyle = { padding: '10px' };
  const inputGroupStyle = { marginBottom: '15px' };
  const labelStyle = { display: 'block', marginBottom: '5px', fontWeight: 'bold' };
  const inputStyle = { width: '100%', padding: '8px', border: '1px solid #ccc', borderRadius: '4px', boxSizing: 'border-box' };
  const checkboxLabelStyle = { marginLeft: '5px' };
  const buttonContainerStyle = { display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '20px' };

  return (
    <form onSubmit={handleSubmit} style={formStyle}>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <div style={inputGroupStyle}>
        <label htmlFor="nomeProduto" style={labelStyle}>Nome:</label>
        <input type="text" id="nomeProduto" value={nome} onChange={(e) => setNome(e.target.value)} required style={inputStyle} />
      </div>
      <div style={inputGroupStyle}>
        <label htmlFor="descricaoProduto" style={labelStyle}>Descrição:</label>
        <textarea id="descricaoProduto" value={descricao} onChange={(e) => setDescricao(e.target.value)} rows={3} style={inputStyle} />
      </div>
      <div style={inputGroupStyle}>
        <label htmlFor="precoBaseProduto" style={labelStyle}>Preço Base (R$):</label>
        <input type="number" id="precoBaseProduto" value={precoBase} onChange={(e) => setPrecoBase(e.target.value)} min="0.01" step="0.01" required style={inputStyle} />
      </div>
      <div style={inputGroupStyle}>
        <label htmlFor="categoriaProduto" style={labelStyle}>Categoria:</label>
        <select id="categoriaProduto" value={categoriaId} onChange={(e) => setCategoriaId(e.target.value)} required style={inputStyle}>
          <option value="">Selecione uma categoria</option>
          {categorias.map(cat => (
            <option key={cat.id} value={cat.id}>{cat.nome}</option>
          ))}
        </select>
      </div>
      <div style={inputGroupStyle}>
        <label htmlFor="ingredientesBase" style={labelStyle}>Ingredientes Base (opcional):</label>
        <input type="text" id="ingredientesBase" value={ingredientesBase} onChange={(e) => setIngredientesBase(e.target.value)} style={inputStyle} />
      </div>
       <div style={inputGroupStyle}>
        <label htmlFor="fotoUrl" style={labelStyle}>URL da Foto (opcional):</label>
        <input type="url" id="fotoUrl" value={fotoUrl} onChange={(e) => setFotoUrl(e.target.value)} style={inputStyle} />
      </div>
      <div style={inputGroupStyle}>
        <input type="checkbox" id="disponivelProduto" checked={disponivel} onChange={(e) => setDisponivel(e.target.checked)} />
        <label htmlFor="disponivelProduto" style={checkboxLabelStyle}>Disponível</label>
      </div>
      <div style={buttonContainerStyle}>
        <button type="button" onClick={onCancel} style={{ padding: '8px 12px', borderRadius: '4px', border: '1px solid #6c757d', backgroundColor: '#6c757d', color: 'white' }}>
          Cancelar
        </button>
        <button type="submit" style={{ padding: '8px 12px', borderRadius: '4px', border: 'none', backgroundColor: '#007bff', color: 'white' }}>
          {produto ? 'Atualizar Produto' : 'Criar Produto'}
        </button>
      </div>
    </form>
  );
};


const GerenciarProdutosPage = () => {
  const [produtos, setProdutos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showFormModal, setShowFormModal] = useState(false);
  const [produtoAtual, setProdutoAtual] = useState(null); // Para edição

  const fetchProdutosECategorias = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [produtosRes, categoriasRes] = await Promise.all([
        adminService.getProductos(),
        adminService.getCategorias()
      ]);
      setProdutos(produtosRes.data || []);
      setCategorias(categoriasRes.data || []);
    } catch (err) {
      console.error("Erro ao buscar dados:", err);
      setError("Falha ao carregar produtos ou categorias.");
      setProdutos([]);
      setCategorias([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProdutosECategorias();
  }, [fetchProdutosECategorias]);

  const handleOpenFormModal = (produto = null) => {
    setProdutoAtual(produto);
    setShowFormModal(true);
  };

  const handleCloseFormModal = () => {
    setProdutoAtual(null);
    setShowFormModal(false);
  };

  const handleSubmitProdutoForm = async (produtoData) => {
    // O try-catch está dentro do ProdutoForm para feedback de erro mais próximo.
    if (produtoAtual) {
      await adminService.updateProducto(produtoAtual.id, produtoData);
    } else {
      await adminService.createProducto(produtoData);
    }
    fetchProdutosECategorias(); // Re-fetch
    handleCloseFormModal();
  };

  const handleDeleteProduto = async (produtoId) => {
    if (window.confirm(`Tem certeza que deseja excluir o produto ID ${produtoId}?`)) {
      try {
        await adminService.deleteProducto(produtoId);
        fetchProdutosECategorias(); // Re-fetch
      } catch (err) {
        console.error("Erro ao excluir produto:", err);
        alert("Erro ao excluir produto: " + (err.response?.data?.detail || err.message));
      }
    }
  };

  const columns = [
    { header: 'ID', key: 'id' },
    { header: 'Nome', key: 'nome' },
    { header: 'Categoria', key: 'categoria_nome' }, // Usando 'categoria_nome' do serializer
    { header: 'Preço Base', key: 'preco_base', render: (row) => `R$ ${parseFloat(row.preco_base).toFixed(2)}` },
    { header: 'Disponível', key: 'disponivel', render: (row) => (row.disponivel ? 'Sim' : 'Não') },
  ];
  
  const pageStyle = { padding: '20px' };
  const buttonStyle = { padding: '10px 15px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', marginBottom: '20px' };

  if (isLoading) return <p style={pageStyle}>Carregando produtos e categorias...</p>;
  if (error) return <p style={{...pageStyle, color: 'red' }}>{error}</p>;

  return (
    <div style={pageStyle}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <h2>Gerenciar Produtos</h2>
        <button onClick={() => handleOpenFormModal()} style={buttonStyle}>
          Novo Produto
        </button>
      </div>
      
      <AdminTable 
        columns={columns} 
        data={produtos} 
        onEdit={handleOpenFormModal}
        onDelete={handleDeleteProduto}
      />

      {showFormModal && (
        <Modal isOpen={showFormModal} onClose={handleCloseFormModal} title={produtoAtual ? 'Editar Produto' : 'Novo Produto'}>
          <ProdutoForm
            produto={produtoAtual}
            categorias={categorias}
            onSubmit={handleSubmitProdutoForm}
            onCancel={handleCloseFormModal}
          />
        </Modal>
      )}
    </div>
  );
};

export default GerenciarProdutosPage;
