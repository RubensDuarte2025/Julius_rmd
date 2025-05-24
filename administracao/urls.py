from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoriaProdutoAdminViewSet, ProdutoAdminViewSet, MesaAdminViewSet,
    ConfiguracaoSistemaViewSet, VendasSimplesRelatorioView, ProdutosVendidosSimplesRelatorioView
)

# Router para os ViewSets de CRUD
admin_router = DefaultRouter()
admin_router.register(r'categorias', CategoriaProdutoAdminViewSet, basename='admin-categoria')
admin_router.register(r'produtos', ProdutoAdminViewSet, basename='admin-produto')
admin_router.register(r'mesas', MesaAdminViewSet, basename='admin-mesa')
admin_router.register(r'configuracoes', ConfiguracaoSistemaViewSet, basename='admin-configuracao')
# Note: Para ConfiguracaoSistemaViewSet, o lookup_field é 'chave'.
# O router gerará URLs como /api/admin/configuracoes/{chave}/

app_name = 'administracao'

urlpatterns = [
    # Incluir as URLs geradas pelo router
    path('', include(admin_router.urls)),

    # URLs para os Relatórios
    path('relatorios/vendas_simples/', VendasSimplesRelatorioView.as_view(), name='relatorio_vendas_simples'),
    path('relatorios/produtos_vendidos_simples/', ProdutosVendidosSimplesRelatorioView.as_view(), name='relatorio_produtos_vendidos_simples'),
]

# URLs Geradas (exemplos):
# Categorias:
#   GET, POST /api/admin/categorias/
#   GET, PUT, PATCH, DELETE /api/admin/categorias/{id}/
# Produtos:
#   GET, POST /api/admin/produtos/
#   GET, PUT, PATCH, DELETE /api/admin/produtos/{id}/
# Mesas:
#   GET, POST /api/admin/mesas/
#   GET, PUT, PATCH, DELETE /api/admin/mesas/{id}/
# Configurações:
#   GET, POST /api/admin/configuracoes/
#   GET, PUT, PATCH, DELETE /api/admin/configuracoes/{chave}/ (usando a chave como lookup)
# Relatórios:
#   GET /api/admin/relatorios/vendas_simples/
#   GET /api/admin/relatorios/produtos_vendidos_simples/
