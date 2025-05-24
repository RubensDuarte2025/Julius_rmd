from django.db import models
from django.utils import timezone
# Assuming 'products' app and its models will be created/available elsewhere
# from products.models import Produto

# For MVP, we might not need a direct ForeignKey to a general 'Pedidos' table
# if the confirmation is manual. We'll store order details in JSON for now.

class PedidoWhatsApp(models.Model):
    """
    Armazena o estado da conversa e o pedido de um cliente via WhatsApp.
    """
    ESTADOS_CONVERSA = [
        ('INICIO', 'Início da conversa'),
        ('AGUARDANDO_OPCAO_INICIAL', 'Aguardando opção inicial (Cardápio/Atendente)'),
        ('AGUARDANDO_ESCOLHA_CATEGORIA', 'Aguardando escolha de categoria'),
        ('AGUARDANDO_ESCOLHA_PRODUTO', 'Aguardando escolha de produto'),
        ('AGUARDANDO_ACAO_CARRINHO', 'Aguardando ação do carrinho (Continuar, Finalizar, Remover)'),
        ('AGUARDANDO_CONFIRMACAO_PEDIDO', 'Aguardando confirmação para finalizar pedido (PIX/Cancelar)'),
        ('AGUARDANDO_CONFIRMACAO_PAGAMENTO_PIX', 'Aguardando confirmação de pagamento PIX (envio de "PAGO")'),
        ('TRANSFERIDO_ATENDENTE', 'Conversa transferida para atendente'),
        ('FINALIZADO', 'Pedido finalizado e informações PIX enviadas'),
    ]

    telefone_cliente = models.CharField(max_length=20, unique=True, help_text="Número de telefone do cliente (ex: +5511999998888)")
    estado_conversa = models.CharField(max_length=50, choices=ESTADOS_CONVERSA, default='INICIO')
    carrinho_atual = models.JSONField(default=dict, help_text="Itens no carrinho, ex: [{'id': 1, 'nome': 'Pizza M', 'preco': 30.00, 'quantidade': 1}]")
    # pedido_confirmado_id = models.ForeignKey('pedidos.Pedido', null=True, blank=True, on_delete=models.SET_NULL) # Pós-MVP
    nome_cliente = models.CharField(max_length=255, blank=True, null=True) # Coletado durante o fluxo
    endereco_entrega = models.TextField(blank=True, null=True) # Coletado durante o fluxo (se aplicável)
    dados_temporarios = models.JSONField(default=dict, blank=True, help_text="Dados temporários para a conversa, como categoria selecionada.")

    # Campos para Cozinha
    STATUS_COZINHA_AGUARDANDO = 'AguardandoPreparo'
    STATUS_COZINHA_EM_PREPARO = 'EmPreparo'
    STATUS_COZINHA_PRONTO = 'Pronto'
    STATUS_COZINHA_ENTREGUE = 'Entregue' # Status final do ciclo da cozinha

    STATUS_COZINHA_CHOICES = [
        (STATUS_COZINHA_AGUARDANDO, 'Aguardando Preparo'),
        (STATUS_COZINHA_EM_PREPARO, 'Em Preparo'),
        (STATUS_COZINHA_PRONTO, 'Pronto'),
        (STATUS_COZINHA_ENTREGUE, 'Entregue'),
    ]
    status_cozinha = models.CharField(
        max_length=20,
        choices=STATUS_COZINHA_CHOICES,
        null=True, blank=True, # Pode ser nulo até o pedido ser confirmado para cozinha
        help_text="Status do pedido na cozinha"
    )
    horario_entrada_cozinha = models.DateTimeField(null=True, blank=True, help_text="Horário que o pedido entrou na fila da cozinha")


    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido WhatsApp de {self.telefone_cliente} - Estado: {self.get_estado_conversa_display()}"

    def reset_conversa(self):
        self.estado_conversa = 'INICIO'
        self.carrinho_atual = [] # Reset to an empty list
        self.dados_temporarios = {} # Reset temporary data
        # Consider if other fields like nome_cliente, endereco_entrega should be reset
        self.save()

    def adicionar_item_carrinho(self, produto, quantidade=1):
        if not isinstance(self.carrinho_atual, list):
            self.carrinho_atual = [] # Ensure it's a list

        # Check if product already in cart to update quantity (more robust)
        for item_no_carrinho in self.carrinho_atual:
            # Ensure product.id is comparable to item_no_carrinho.get('id')
            # Product might be a mock object or a Django model instance
            produto_id = getattr(produto, 'id', None)
            if produto_id is not None and item_no_carrinho.get('id') == produto_id:
                item_no_carrinho['quantidade'] = item_no_carrinho.get('quantidade', 0) + quantidade
                self.save()
                return

        # If not in cart, add new item
        self.carrinho_atual.append({
            'id': getattr(produto, 'id', None), # Handle mock or real Product object
            'nome': getattr(produto, 'nome', 'Produto Desconhecido'),
            'preco': float(getattr(produto, 'preco', 0.0)), # Use 'preco' as per MOCKED_PRODUCTS
            'quantidade': quantidade
        })
        self.save()

    def remover_ultimo_item_carrinho(self):
        if isinstance(self.carrinho_atual, list) and self.carrinho_atual:
            self.carrinho_atual.pop()
            self.save()
            return True
        return False

    def formatar_carrinho_para_mensagem(self):
        if not isinstance(self.carrinho_atual, list) or not self.carrinho_atual:
            return "Seu carrinho está vazio."
        
        linhas_itens = ["Seu pedido atual:"]
        for i, item in enumerate(self.carrinho_atual):
            linhas_itens.append(f"{i+1}. {item.get('quantidade', 1)}x {item.get('nome', 'N/A')} - R${item.get('preco', 0.00):.2f} cada")
        return "\n".join(linhas_itens)

    def calcular_total_carrinho(self):
        if not isinstance(self.carrinho_atual, list):
            return 0.0
        total = 0.0
        for item in self.carrinho_atual:
            total += item.get('preco', 0.0) * item.get('quantidade', 1)
        return total

    class Meta:
        verbose_name = "Pedido WhatsApp"
        verbose_name_plural = "Pedidos WhatsApp"
        ordering = ['-data_atualizacao']
