from rest_framework import serializers
from .models import Pagamento

class PagamentoSerializer(serializers.ModelSerializer):
    # Para exibir o tipo de pedido de forma mais legível
    tipo_pedido_display = serializers.SerializerMethodField()
    # Para exibir o objeto do pedido de forma mais legível (ex: Mesa N, Cliente X)
    # Isso pode ser mais complexo e pode exigir acesso ao objeto real do pedido.
    # Para MVP, podemos apenas mostrar o ID e o tipo.
    pedido_info = serializers.SerializerMethodField()

    class Meta:
        model = Pagamento
        fields = [
            'id', 'tipo_pedido_display', 'pedido_info', 'object_id', 
            'metodo_pagamento', 'get_metodo_pagamento_display',
            'valor_pago', 'status_pagamento', 'get_status_pagamento_display',
            'data_hora_pagamento', 'transacao_id_gateway', 'qr_code_pix_copia_cola',
            'data_criacao_registro', 'data_atualizacao_registro'
        ]
        # Adicionar get_..._display para campos com choices
        # depth = 1 # Cuidado com depth, pode expor muitos dados. Melhor ser explícito.

    def get_tipo_pedido_display(self, obj):
        if obj.content_type:
            return obj.content_type.model_class()._meta.verbose_name.title()
        return None

    def get_pedido_info(self, obj):
        if obj.pedido:
            # Tentar obter uma representação string do pedido
            # Se o pedido for PedidoMesa, pode ser "Mesa X"
            # Se for PedidoWhatsApp, pode ser o telefone do cliente
            # Isso requer que os modelos referenciados tenham um __str__ informativo.
            return str(obj.pedido)
        return f"{self.get_tipo_pedido_display(obj)} ID: {obj.object_id}"
