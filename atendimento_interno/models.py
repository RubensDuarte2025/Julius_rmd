from django.db import models
from django.utils import timezone
# from products.models import Produto # Assume this will exist in a 'products' app

# Placeholder for Produto if the app/model doesn't exist yet for relationships
# This helps in defining ForeignKeys without immediate dependency.
# In a real setup, 'products.Produto' would be used directly.
class Produto(models.Model):
    nome = models.CharField(max_length=100)
    preco_base = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.nome

    class Meta:
        # This ensures this mock model doesn't create a table if 'products' app handles it
        # managed = False # Temporarily comment out if we need to run makemigrations for this app alone first
        verbose_name = "Produto (Placeholder)"


class Mesa(models.Model):
    STATUS_LIVRE = 'Livre'
    STATUS_OCUPADA = 'Ocupada'
    STATUS_AGUARDANDO_PAGAMENTO = 'AguardandoPagamento'
    STATUS_INTERDITADA = 'Interditada'

    STATUS_CHOICES = [
        (STATUS_LIVRE, 'Livre'),
        (STATUS_OCUPADA, 'Ocupada'),
        (STATUS_AGUARDANDO_PAGAMENTO, 'Aguardando Pagamento'),
        (STATUS_INTERDITADA, 'Interditada'),
    ]

    numero_identificador = models.CharField(max_length=10, unique=True, help_text="Número ou nome da mesa (ex: 01, 02, Varanda 1)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_LIVRE)
    capacidade_default = models.PositiveIntegerField(default=4)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Mesa {self.numero_identificador} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Mesa"
        verbose_name_plural = "Mesas"
        ordering = ['numero_identificador']


class PedidoMesa(models.Model):
    STATUS_ABERTO = 'Aberto'
    STATUS_FECHADO = 'Fechado' # Fechado para novos itens, aguardando pagamento
    STATUS_PAGO = 'Pago'
    STATUS_CANCELADO = 'Cancelado'

    STATUS_PEDIDO_CHOICES = [
        (STATUS_ABERTO, 'Aberto'),
        (STATUS_FECHADO, 'Fechado'),
        (STATUS_PAGO, 'Pago'),
        (STATUS_CANCELADO, 'Cancelado'),
    ]

    mesa = models.ForeignKey(Mesa, on_delete=models.PROTECT, related_name='pedidos') # Proteger mesa se tiver pedidos
    status_pedido = models.CharField(max_length=20, choices=STATUS_PEDIDO_CHOICES, default=STATUS_ABERTO)
    data_abertura = models.DateTimeField(default=timezone.now)
    data_fechamento = models.DateTimeField(null=True, blank=True)
    observacoes_gerais = models.TextField(blank=True, null=True)
    
    # For MVP, payment details directly on the order
    METODO_PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('cartao_maquineta', 'Cartão (Maquineta)'),
        ('pix_maquineta', 'PIX (Maquineta)'),
    ]
    metodo_pagamento_registrado = models.CharField(max_length=20, choices=METODO_PAGAMENTO_CHOICES, null=True, blank=True)
    valor_pago_registrado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Campos para Cozinha
    STATUS_COZINHA_AGUARDANDO = 'AguardandoPreparo'
    STATUS_COZINHA_EM_PREPARO = 'EmPreparo'
    STATUS_COZINHA_PRONTO = 'Pronto'
    STATUS_COZINHA_ENTREGUE = 'Entregue' # Status final do ciclo da cozinha (ex: entregue ao cliente/garçom)

    STATUS_COZINHA_CHOICES = [
        (STATUS_COZINHA_AGUARDANDO, 'Aguardando Preparo'),
        (STATUS_COZINHA_EM_PREPARO, 'Em Preparo'),
        (STATUS_COZINHA_PRONTO, 'Pronto'),
        (STATUS_COZINHA_ENTREGUE, 'Entregue'),
    ]
    status_cozinha = models.CharField(
        max_length=20,
        choices=STATUS_COZINHA_CHOICES,
        null=True, blank=True, # Pode ser nulo até o pedido ser efetivamente enviado para cozinha
        help_text="Status do pedido na cozinha"
    )
    horario_entrada_cozinha = models.DateTimeField(null=True, blank=True, help_text="Horário que o pedido entrou na fila da cozinha")


    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido {self.id} - Mesa {self.mesa.numero_identificador} ({self.get_status_pedido_display()})"

    def calcular_total(self):
        return sum(item.subtotal_item for item in self.itens_pedido.all())

    class Meta:
        verbose_name = "Pedido de Mesa"
        verbose_name_plural = "Pedidos de Mesa"
        ordering = ['-data_abertura']


class ItemPedidoMesa(models.Model):
    pedido_mesa = models.ForeignKey(PedidoMesa, on_delete=models.CASCADE, related_name='itens_pedido')
    # produto = models.ForeignKey('products.Produto', on_delete=models.PROTECT) # Use string if 'products' app is defined later
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, help_text="Produto selecionado para este item")
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario_no_momento = models.DecimalField(max_digits=10, decimal_places=2, help_text="Preço do produto no momento da adição ao pedido")
    subtotal_item = models.DecimalField(max_digits=10, decimal_places=2, help_text="Calculado como quantidade * preco_unitario_no_momento")
    observacoes_item = models.TextField(blank=True, null=True)

    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Ensure subtotal is calculated on save
        if self.preco_unitario_no_momento is not None: # Check to avoid error if price not set yet
             self.subtotal_item = self.quantidade * self.preco_unitario_no_momento
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} no Pedido {self.pedido_mesa.id}"

    class Meta:
        verbose_name = "Item de Pedido de Mesa"
        verbose_name_plural = "Itens de Pedidos de Mesa"
        unique_together = ('pedido_mesa', 'produto') # Simplification: one entry per product, update quantity. Or allow multiple with different obs? For MVP, one entry.
        ordering = ['data_criacao']
