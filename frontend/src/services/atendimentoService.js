import apiClient from './api'; // apiClient from previous setup

const atendimentoService = {
  getMesas: () => {
    return apiClient.get('/mesas/');
  },

  getMesaDetalhes: (mesaId) => {
    // This might not be strictly needed if getMesas() returns enough detail,
    // or if the main interaction point is the active pedido on a mesa.
    // The backend /api/mesas/{mesaId}/ already returns pedidos_recentes.
    return apiClient.get(`/mesas/${mesaId}/`);
  },

  // Renamed from criarPedidoParaMesa to getOrCreateActivePedidoForMesa for clarity
  // This assumes the backend endpoint POST /api/mesas/{mesaId}/pedidos/
  // will either create a new 'Aberto' pedido if none exists (or last one is 'Pago'/'Cancelado')
  // or return the currently 'Aberto' or 'Fechado' (awaiting payment) pedido.
  // The backend view MesaViewSet.criar_pedido_para_mesa was designed to create or return existing.
  getOrCreateActivePedidoForMesa: (mesaId) => {
    return apiClient.post(`/mesas/${mesaId}/pedidos/`, {}); // Empty payload for creation
  },

  getPedidoMesaDetalhes: (pedidoId) => {
    return apiClient.get(`/pedidos_mesa/${pedidoId}/`);
  },

  adicionarItemAoPedido: (pedidoId, itemData) => {
    // itemData: { produto_id: id, quantidade: X, observacoes_item: "obs" (opcional) }
    // The backend for POST /pedidos_mesa/{pedido_id}/itens/ expects produto_id and quantidade.
    // preco_unitario_no_momento is usually set by backend based on produto_id.
    return apiClient.post(`/pedidos_mesa/${pedidoId}/itens/`, itemData);
  },

  removerItemDoPedido: (pedidoId, itemId) => {
    // Note: The URL structure in the backend was:
    // DELETE /api/pedidos_mesa/{pedido_mesa_pk}/itens/{item_pk}/
    return apiClient.delete(`/pedidos_mesa/${pedidoId}/itens/${itemId}/`);
  },

  registrarPagamentoPedido: (pedidoId, pagamentoData) => {
    // pagamentoData: { metodo: "dinheiro", valor_pago: 123.45 }
    return apiClient.post(`/pedidos_mesa/${pedidoId}/registrar-pagamento/`, pagamentoData);
  },

  getProductos: () => {
    // Using the admin endpoint for products as specified.
    // Ensure this endpoint is accessible for attendants (permissions might be needed on backend).
    return apiClient.get('/admin/produtos/');
  },
  
  atualizarStatusMesa: (mesaId, statusData) => {
    // statusData: { status: "Livre" / "Interditada" etc. }
    return apiClient.patch(`/mesas/${mesaId}/atualizar-status/`, statusData);
  },

  // Helper to update order status (e.g., to 'Fechado' before payment)
  // PATCH /api/pedidos_mesa/{pedido_id}/
  // This uses PedidoMesaUpdateSerializer on the backend
  atualizarStatusPedidoMesa: (pedidoId, pedidoStatusData) => {
    // pedidoStatusData: { status_pedido: "Fechado", observacoes_gerais: "obs" (opcional) }
    return apiClient.patch(`/pedidos_mesa/${pedidoId}/`, pedidoStatusData);
  }
};

export default atendimentoService;
