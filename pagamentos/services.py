from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from .models import Pagamento
# Importar modelos de pedido para type hinting, se desejado, mas não estritamente necessário para GenericForeignKey
# from whatsapp_bot.models import PedidoWhatsApp
# from atendimento_interno.models import PedidoMesa

def registrar_pagamento_para_pedido(
    pedido_obj, # Instância de PedidoWhatsApp ou PedidoMesa
    metodo_pagamento: str,
    valor_pago: float, # Ou Decimal
    status_pagamento: str = Pagamento.STATUS_APROVADO, # Default para aprovado em MVP
    data_hora_pagamento=None,
    transacao_id_gateway: str = None,
    qr_code_pix: str = None
) -> Pagamento:
    """
    Cria um registro de Pagamento para um pedido específico (PedidoWhatsApp ou PedidoMesa).

    Args:
        pedido_obj: A instância do modelo do pedido (ex: PedidoWhatsApp, PedidoMesa).
        metodo_pagamento: String do método de pagamento (ver Pagamento.METODO_PAGAMENTO_CHOICES).
        valor_pago: O valor que foi pago.
        status_pagamento: Status do pagamento (default: Aprovado).
        data_hora_pagamento: Data e hora do pagamento (default: agora).
        transacao_id_gateway: ID da transação do gateway (opcional).
        qr_code_pix: QR code ou chave PIX (opcional).

    Returns:
        A instância do Pagamento criada.

    Raises:
        ValueError: Se o pedido_obj for inválido ou não tiver um ID.
    """
    if not hasattr(pedido_obj, 'id') or not pedido_obj.id:
        raise ValueError("Objeto do pedido inválido ou sem ID.")

    content_type = ContentType.objects.get_for_model(pedido_obj.__class__)
    
    if data_hora_pagamento is None:
        data_hora_pagamento = timezone.now()

    pagamento = Pagamento.objects.create(
        content_type=content_type,
        object_id=pedido_obj.id,
        metodo_pagamento=metodo_pagamento,
        valor_pago=valor_pago,
        status_pagamento=status_pagamento,
        data_hora_pagamento=data_hora_pagamento,
        transacao_id_gateway=transacao_id_gateway,
        qr_code_pix_copia_cola=qr_code_pix
    )

    # Lógica adicional Pós-Criação de Pagamento (ex: atualizar status do pedido original)
    # Esta lógica pode ser mais complexa e variar dependendo do tipo de pedido.
    # Por enquanto, a responsabilidade de atualizar o status do pedido PAI
    # (PedidoWhatsApp.status_pedido, PedidoMesa.status_pedido)
    # permanece nas views dos respectivos apps, mas o Pagamento está registrado.

    # Exemplo (Pós-MVP ou se centralizar aqui):
    # if status_pagamento == Pagamento.STATUS_APROVADO:
    #     if isinstance(pedido_obj, PedidoWhatsApp):
    #         # pedido_obj.status_pedido = PedidoWhatsApp.STATUS_PAGO (ou similar)
    #         # pedido_obj.save()
    #         pass
    #     elif isinstance(pedido_obj, PedidoMesa):
    #         # pedido_obj.status_pedido = PedidoMesa.STATUS_PAGO
    #         # pedido_obj.mesa.status = Mesa.STATUS_LIVRE (se for o caso)
    #         # pedido_obj.save()
    #         # pedido_obj.mesa.save()
    #         pass
            
    return pagamento

# Outros serviços podem ser adicionados aqui, como:
# - consultar_status_pagamento_gateway(pagamento_id) (Pós-MVP)
# - processar_reembolso(pagamento_id, valor_reembolso) (Pós-MVP)
