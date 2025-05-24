from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from rest_framework_nested import routers # Alternative for more complex nesting

from .views import MesaViewSet, PedidoMesaViewSet, ItemPedidoMesaViewSet

# Router principal para Mesas e PedidosMesa (nível superior)
router = DefaultRouter()
router.register(r'mesas', MesaViewSet, basename='mesa')
router.register(r'pedidos_mesa', PedidoMesaViewSet, basename='pedidomesa')
# router.register(r'itens_pedido_mesa', ItemPedidoMesaViewSet, basename='itempedidomesa') # For /api/itens_pedido_mesa/{item_id}/

# URLs para Itens de Pedido aninhados sob Pedidos de Mesa
# GET /api/pedidos_mesa/{pedido_mesa_pk}/itens/  (Listar itens de um pedido)
# POST /api/pedidos_mesa/{pedido_mesa_pk}/itens/ (Adicionar item a um pedido)
pedido_itens_list = ItemPedidoMesaViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

# URLs para um item específico (usando o router base para ItemPedidoMesa)
# GET /api/itens_pedido_mesa/{pk}/ (Detalhe do item)
# PUT /api/itens_pedido_mesa/{pk}/ (Atualizar item)
# PATCH /api/itens_pedido_mesa/{pk}/ (Atualizar parcialmente item)
# DELETE /api/itens_pedido_mesa/{pk}/ (Remover item)
# O router.register para 'itens_pedido_mesa' acima já cuidaria disso.
# No entanto, a especificação da API é:
# PUT /api/pedidos_mesa/{pedido_id}/itens/{item_id}/
# DELETE /api/pedidos_mesa/{pedido_id}/itens/{item_id}/
# Isso requer uma configuração de rota mais aninhada.

# Para MVP, vamos simplificar e usar URLs separadas se o aninhamento completo for complexo sem drf-nested-routers:
# 1. Listar/Criar itens para um pedido: /api/pedidos_mesa/{pedido_mesa_pk}/itens/
# 2. Operações em item específico: /api/itens_pedido_mesa/{item_pk}/ (GET, PUT, DELETE)

# Router para itens_pedido_mesa (para operações diretas no item como PUT, DELETE por ID do item)
# Este router é separado para permitir URLs como /api/itens_pedido_mesa/{item_id}/
item_router = DefaultRouter()
item_router.register(r'itens_pedido_mesa', ItemPedidoMesaViewSet, basename='itempedidomesa')


app_name = 'atendimento_interno'

urlpatterns = [
    path('', include(router.urls)), # Inclui /api/mesas/, /api/pedidos_mesa/
    path('', include(item_router.urls)), # Inclui /api/itens_pedido_mesa/{item_id}/

    # Rota para listar itens de um pedido específico e adicionar novo item a um pedido
    # GET, POST -> /api/pedidos_mesa/{pedido_mesa_pk}/itens/
    path('pedidos_mesa/<int:pedido_mesa_pk>/itens/', pedido_itens_list, name='pedido-itens-list'),

    # Para as operações PUT e DELETE em itens específicos DENTRO de um pedido (mais RESTful e alinhado com a especificação)
    # PUT /api/pedidos_mesa/{pedido_mesa_pk}/itens/{item_pk}/
    # DELETE /api/pedidos_mesa/{pedido_mesa_pk}/itens/{item_pk}/
    path('pedidos_mesa/<int:pedido_mesa_pk>/itens/<int:pk>/', ItemPedidoMesaViewSet.as_view({
        'get': 'retrieve', # Opcional, se quiser buscar item específico neste endpoint
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='pedido-item-detail'),
]


# Explicação das URLs geradas e como elas se alinham com a especificação:
#
# Mesas:
#   GET /api/mesas/                             -> MesaViewSet.list()
#   POST /api/mesas/                            -> MesaViewSet.create()
#   GET /api/mesas/{mesa_id}/                   -> MesaViewSet.retrieve()
#   PUT /api/mesas/{mesa_id}/                   -> MesaViewSet.update()
#   PATCH /api/mesas/{mesa_id}/                 -> MesaViewSet.partial_update()
#   DELETE /api/mesas/{mesa_id}/                -> MesaViewSet.destroy()
#   PATCH /api/mesas/{mesa_id}/atualizar-status/-> MesaViewSet.atualizar_status() (Custom Action)
#   POST /api/mesas/{mesa_id}/pedidos/          -> MesaViewSet.criar_pedido_para_mesa() (Custom Action)
#
# Pedidos de Mesa (geral):
#   GET /api/pedidos_mesa/                      -> PedidoMesaViewSet.list()
#   POST /api/pedidos_mesa/                     -> PedidoMesaViewSet.create() (Cria pedido sem mesa específica, pode não ser usado)
#   GET /api/pedidos_mesa/{pedido_id}/          -> PedidoMesaViewSet.retrieve()
#   PUT /api/pedidos_mesa/{pedido_id}/          -> PedidoMesaViewSet.update()
#   PATCH /api/pedidos_mesa/{pedido_id}/        -> PedidoMesaViewSet.partial_update()
#   DELETE /api/pedidos_mesa/{pedido_id}/       -> PedidoMesaViewSet.destroy()
#   POST /api/pedidos_mesa/{pedido_id}/registrar-pagamento/ -> PedidoMesaViewSet.registrar_pagamento() (Custom Action)
#
# Itens do Pedido de Mesa (aninhado e direto):
#   GET /api/pedidos_mesa/{pedido_mesa_pk}/itens/     -> ItemPedidoMesaViewSet.list() (filtrado para pedido_mesa_pk)
#   POST /api/pedidos_mesa/{pedido_mesa_pk}/itens/    -> ItemPedidoMesaViewSet.create() (associado com pedido_mesa_pk)
#
#   GET /api/pedidos_mesa/{pedido_mesa_pk}/itens/{pk}/    -> ItemPedidoMesaViewSet.retrieve() (item pk dentro do pedido_mesa_pk)
#   PUT /api/pedidos_mesa/{pedido_mesa_pk}/itens/{pk}/    -> ItemPedidoMesaViewSet.update() (item pk dentro do pedido_mesa_pk)
#   PATCH /api/pedidos_mesa/{pedido_mesa_pk}/itens/{pk}/  -> ItemPedidoMesaViewSet.partial_update() (item pk dentro do pedido_mesa_pk)
#   DELETE /api/pedidos_mesa/{pedido_mesa_pk}/itens/{pk}/ -> ItemPedidoMesaViewSet.destroy() (item pk dentro do pedido_mesa_pk)
#
#   As URLs /api/itens_pedido_mesa/... (do item_router) também estarão disponíveis,
#   mas as aninhadas acima são mais específicas e RESTful para o contexto do pedido.
#   Para o MVP, a especificação pede:
#   - POST /api/pedidos_mesa/{pedido_id}/itens/ (coberto)
#   - PUT /api/pedidos_mesa/{pedido_id}/itens/{item_id}/ (coberto pela rota aninhada com pk)
#   - DELETE /api/pedidos_mesa/{pedido_id}/itens/{item_id}/ (coberto pela rota aninhada com pk)
#
#   O ItemPedidoMesaViewSet foi configurado em views.py para esperar 'pedido_mesa_pk' no self.kwargs
#   para list() e create(), e 'pk' (id do item) para retrieve(), update(), destroy().
#   A última rota aninhada ('pedido-item-detail') garante que 'pk' (item_id) e 'pedido_mesa_pk' (pedido_id)
#   estejam disponíveis para o ItemPedidoMesaViewSet.
#   A view precisará ser ajustada para usar `self.kwargs.get('pk')` para o item e `self.kwargs.get('pedido_mesa_pk')` para o pedido.
#   No ItemPedidoMesaViewSet, get_queryset já usa `pedido_mesa_pk`.
#   Para retrieve, update, destroy, o `pk` é o ID do item, e o `pedido_mesa_pk` pode ser usado para validação adicional se necessário.
#
#   A lógica em ItemPedidoMesaViewSet.perform_destroy e perform_update já valida o status do pedido_mesa.
#   Se precisarmos garantir que o item {pk} realmente pertence ao {pedido_mesa_pk} na URL para update/delete,
#   o método get_object do ItemPedidoMesaViewSet pode ser sobrescrito:
#   def get_object(self):
#       queryset = self.get_queryset() # Isso já filtra por pedido_mesa_pk se ele estiver na URL da lista
#       # Para rotas de detalhe do item, o queryset padrão não é filtrado por pedido_mesa_pk
#       # Portanto, precisamos filtrar aqui também.
#       obj = get_object_or_404(ItemPedidoMesa, pk=self.kwargs['pk'], pedido_mesa_id=self.kwargs['pedido_mesa_pk'])
#       self.check_object_permissions(self.request, obj)
#       return obj
#   Isso será adicionado na view para consistência.

# O Django REST Framework não lida com aninhamento de rotas no DefaultRouter nativamente da forma que
# `drf-nested-routers` faz. A abordagem acima com paths manuais para as ações aninhadas
# é uma forma de alcançar a estrutura de URL desejada.
# A `basename` no router é importante para a geração de `reverse` URL lookups.
# As rotas manuais também têm `name`.
# O `item_router` separado para `/api/itens_pedido_mesa/` é redundante se as aninhadas cobrem tudo,
# mas foi mantido para o caso de alguma view precisar de acesso direto ao item sem contexto de pedido.
# Para MVP, podemos remover as rotas do `item_router` se as aninhadas forem suficientes.
# Vamos remover o `item_router` para evitar confusão e focar nas URLs especificadas.
urlpatterns = [
    path('', include(router.urls)), # Inclui /api/mesas/, /api/pedidos_mesa/
    path('pedidos_mesa/<int:pedido_mesa_pk>/itens/', pedido_itens_list, name='pedido-itens-list'),
    path('pedidos_mesa/<int:pedido_mesa_pk>/itens/<int:pk>/', ItemPedidoMesaViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='pedido-item-detail'),
]
