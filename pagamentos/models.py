from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

class Pagamento(models.Model):
    METODO_PIX = 'pix'
    METODO_CARTAO_CREDITO_ONLINE = 'cartao_credito_online' # Pós-MVP
    METODO_CARTAO_DEBITO_MAQUINETA = 'cartao_debito_maquineta'
    METODO_CARTAO_CREDITO_MAQUINETA = 'cartao_credito_maquineta'
    METODO_DINHEIRO = 'dinheiro'
    METODO_OUTRO = 'outro'

    METODO_PAGAMENTO_CHOICES = [
        (METODO_PIX, 'PIX'),
        (METODO_CARTAO_CREDITO_ONLINE, 'Cartão de Crédito Online'),
        (METODO_CARTAO_DEBITO_MAQUINETA, 'Cartão de Débito (Maquineta)'),
        (METODO_CARTAO_CREDITO_MAQUINETA, 'Cartão de Crédito (Maquineta)'),
        (METODO_DINHEIRO, 'Dinheiro'),
        (METODO_OUTRO, 'Outro'),
    ]

    STATUS_PENDENTE = 'Pendente'
    STATUS_APROVADO = 'Aprovado'
    STATUS_RECUSADO = 'Recusado'
    STATUS_REEMBOLSADO = 'Reembolsado'

    STATUS_PAGAMENTO_CHOICES = [
        (STATUS_PENDENTE, 'Pendente'),
        (STATUS_APROVADO, 'Aprovado'),
        (STATUS_RECUSADO, 'Recusado'),
        (STATUS_REEMBOLSADO, 'Reembolsado'),
    ]

    # Campos para GenericForeignKey, permitindo linkar com PedidoWhatsApp ou PedidoMesa
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Tipo do objeto do pedido (PedidoWhatsApp ou PedidoMesa)"
    )
    object_id = models.PositiveIntegerField(help_text="ID do objeto do pedido")
    pedido = GenericForeignKey('content_type', 'object_id')

    metodo_pagamento = models.CharField(
        max_length=50,
        choices=METODO_PAGAMENTO_CHOICES,
        default=METODO_OUTRO
    )
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2)
    status_pagamento = models.CharField(
        max_length=20,
        choices=STATUS_PAGAMENTO_CHOICES,
        default=STATUS_PENDENTE
    )
    data_hora_pagamento = models.DateTimeField(default=timezone.now, help_text="Data e hora em que o pagamento foi registrado/confirmado")
    
    # Campos opcionais
    transacao_id_gateway = models.CharField(max_length=255, blank=True, null=True, help_text="ID da transação no gateway de pagamento externo")
    qr_code_pix_copia_cola = models.TextField(blank=True, null=True, help_text="QR Code PIX (copia e cola) para pagamentos PIX")
    # link_pagamento_cartao = models.URLField(max_length=2048, blank=True, null=True) # Pós-MVP

    data_criacao_registro = models.DateTimeField(auto_now_add=True)
    data_atualizacao_registro = models.DateTimeField(auto_now=True)

    def __str__(self):
        pedido_repr = 'Pedido Desconhecido'
        if self.pedido:
            pedido_repr = f"{self.content_type.model.replace('pedido', '')} ID {self.object_id}"
        return f"Pagamento {self.id} para {pedido_repr} - R${self.valor_pago} ({self.get_status_pagamento_display()})"

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ['-data_hora_pagamento']
        # Index para consultas por GenericForeignKey
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
