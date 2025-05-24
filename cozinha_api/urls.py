from django.urls import path
from .views import PedidosParaPrepararListView, AtualizarStatusCozinhaView

app_name = 'cozinha_api'

urlpatterns = [
    path('pedidos_para_preparar/', PedidosParaPrepararListView.as_view(), name='pedidos_para_preparar_list'),
    path('pedidos/<str:tipo_origem>/<int:id_pedido_origem>/status/', AtualizarStatusCozinhaView.as_view(), name='atualizar_status_cozinha'),
]
