import apiClient from './api'; // apiClient from previous setup

const cozinhaService = {
  getPedidosParaPreparar: () => {
    return apiClient.get('/cozinha/pedidos_para_preparar/');
  },

  atualizarStatusPedidoCozinha: (tipoOrigem, idPedidoOrigem, statusCozinha) => {
    // O backend espera um payload { "status_cozinha": "NovoStatus" }
    const payload = { status_cozinha: statusCozinha };
    return apiClient.patch(`/cozinha/pedidos/${tipoOrigem}/${idPedidoOrigem}/status/`, payload);
  },
};

export default cozinhaService;
