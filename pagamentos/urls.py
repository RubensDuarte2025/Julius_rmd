from django.urls import path
from .views import ListarPagamentosPorPedidoView

app_name = 'pagamentos'

urlpatterns = [
    path('pedido/<str:tipo_origem>/<int:id_pedido_origem>/', ListarPagamentosPorPedidoView.as_view(), name='listar_pagamentos_por_pedido'),
    # Outras URLs específicas do app de pagamentos podem ser adicionadas aqui no futuro,
    # por exemplo, para webhooks de gateways de pagamento (Pós-MVP).
]
