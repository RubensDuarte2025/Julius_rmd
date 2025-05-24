import apiClient from './api'; // apiClient from a previous setup

const adminService = {
  // Categorias
  getCategorias: () => apiClient.get('/admin/categorias/'),
  createCategoria: (data) => apiClient.post('/admin/categorias/', data),
  updateCategoria: (id, data) => apiClient.put(`/admin/categorias/${id}/`, data),
  deleteCategoria: (id) => apiClient.delete(`/admin/categorias/${id}/`),

  // Produtos
  getProductos: () => apiClient.get('/admin/produtos/'),
  getProducto: (id) => apiClient.get(`/admin/produtos/${id}/`),
  createProducto: (data) => {
    // For MVP, assuming JSON data. FormData for file uploads would be:
    // return apiClient.post('/admin/produtos/', data, { headers: { 'Content-Type': 'multipart/form-data' } });
    return apiClient.post('/admin/produtos/', data);
  },
  updateProducto: (id, data) => {
    // Similar consideration for FormData if/when photo upload is added
    return apiClient.put(`/admin/produtos/${id}/`, data);
  },
  deleteProducto: (id) => apiClient.delete(`/admin/produtos/${id}/`),

  // Mesas
  getMesas: () => apiClient.get('/admin/mesas/'),
  createMesa: (data) => apiClient.post('/admin/mesas/', data),
  updateMesa: (id, data) => apiClient.put(`/admin/mesas/${id}/`, data),
  deleteMesa: (id) => apiClient.delete(`/admin/mesas/${id}/`),

  // Configurações
  getConfiguracoes: () => apiClient.get('/admin/configuracoes/'),
  // Backend uses 'chave' as lookup_field for configuracoes
  updateConfiguracao: (chave, data) => apiClient.put(`/admin/configuracoes/${chave}/`, data),
  // createConfiguracao and deleteConfiguracao might be disabled on backend or less common.
  // If needed:
  // createConfiguracao: (data) => apiClient.post('/admin/configuracoes/', data),
  // deleteConfiguracao: (chave) => apiClient.delete(`/admin/configuracoes/${chave}/`),


  // Relatórios
  getRelatorioVendas: (params) => {
    // params: { data_inicio: 'YYYY-MM-DD', data_fim: 'YYYY-MM-DD' }
    return apiClient.get('/admin/relatorios/vendas_simples/', { params });
  },
  getRelatorioProdutosVendidos: (params) => {
    return apiClient.get('/admin/relatorios/produtos_vendidos_simples/', { params });
  },
};

export default adminService;
