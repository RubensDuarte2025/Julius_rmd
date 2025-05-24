from django.contrib import admin
from .models import ConfiguracaoSistema # Placeholder for Produto, CategoriaProduto if defined here

# Register your models here.
@admin.register(ConfiguracaoSistema)
class ConfiguracaoSistemaAdmin(admin.ModelAdmin):
    list_display = ('chave', 'valor', 'descricao')
    search_fields = ('chave', 'descricao')
    ordering = ('chave',)

# Placeholder for registering Product/Category if they were defined in this app's models.py
# If they are in a separate 'products' app, they should be registered in 'products/admin.py'.
# from .models import ProdutoPlaceholder, CategoriaProdutoPlaceholder
# @admin.register(ProdutoPlaceholder)
# class ProdutoPlaceholderAdmin(admin.ModelAdmin):
#     list_display = ('nome', 'categoria', 'preco_base', 'disponivel')
#     list_filter = ('disponivel', 'categoria')
#     search_fields = ('nome', 'descricao')

# @admin.register(CategoriaProdutoPlaceholder)
# class CategoriaProdutoPlaceholderAdmin(admin.ModelAdmin):
#     list_display = ('nome', 'descricao')
#     search_fields = ('nome',)
