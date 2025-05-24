from django.db import models

class ConfiguracaoSistema(models.Model):
    chave = models.CharField(max_length=100, unique=True, help_text="Chave única para a configuração (ex: NOME_PIZZARIA)")
    valor = models.TextField(help_text="Valor da configuração")
    descricao = models.TextField(blank=True, null=True, help_text="Descrição do que esta configuração controla")

    def __str__(self):
        return f"{self.chave} = {self.valor}"

    class Meta:
        verbose_name = "Configuração do Sistema"
        verbose_name_plural = "Configurações do Sistema"
        ordering = ['chave']

# --- Placeholder Models for Produto e CategoriaProduto ---
# Estes modelos são definidos aqui temporariamente para permitir o desenvolvimento
# das APIs de administração de cardápio. Idealmente, eles residiriam em um
# app dedicado como 'products'. Se esse app for criado, estes placeholders
# devem ser removidos e as dependências ajustadas.

class CategoriaProdutoPlaceholder(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Categoria de Produto (Placeholder)"
        verbose_name_plural = "Categorias de Produtos (Placeholder)"
        # managed = False # Se um app 'products' gerenciar esta tabela, descomente
        db_table = 'products_categoriaproduto' # Exemplo de nome de tabela se gerenciado por outro app

class ProdutoPlaceholder(models.Model):
    categoria = models.ForeignKey(
        CategoriaProdutoPlaceholder, 
        on_delete=models.SET_NULL, # Ou models.PROTECT, dependendo da regra de negócio
        null=True, blank=True, # Permitir produto sem categoria temporariamente ou para casos especiais
        related_name='produtos'
    )
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)
    preco_base = models.DecimalField(max_digits=10, decimal_places=2)
    foto_url = models.URLField(max_length=2048, blank=True, null=True) # Opcional
    disponivel = models.BooleanField(default=True)
    ingredientes_base = models.TextField(blank=True, null=True, help_text="Lista simples de ingredientes base para MVP")
    # Outros campos como tempo_preparo_estimado podem ser adicionados aqui.

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Produto (Placeholder)"
        verbose_name_plural = "Produtos (Placeholder)"
        # managed = False # Se um app 'products' gerenciar esta tabela, descomente
        db_table = 'products_produto' # Exemplo de nome de tabela se gerenciado por outro app
        ordering = ['nome']

# É importante que, se um app 'products' for criado, ele defina os modelos
# CategoriaProduto e Produto, e este app 'administracao' então os importe
# diretamente em seus serializers e views, em vez de usar estes placeholders.
# As migrations para estes modelos placeholder só devem ser criadas e aplicadas
# se o app 'products' não existir ou não for ser criado imediatamente.
# Se o app 'products' já existir, estes modelos são redundantes e não devem ser usados.
# Por enquanto, para permitir o desenvolvimento da API de administração, eles são incluídos.
# E a diretiva 'managed = False' seria crucial se as tabelas já existirem e forem gerenciadas por outro app.
# Para este exercício, vou assumir que preciso criar estas tabelas a partir daqui, então 'managed = True' (padrão).
