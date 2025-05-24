from rest_framework import serializers
from whatsapp_bot.models import PedidoWhatsApp
from atendimento_interno.models import PedidoMesa, ItemPedidoMesa # Assuming ItemPedidoMesa has product name and observations

# Serializer for individual items within a consolidated order
class ItemConsolidadoSerializer(serializers.Serializer):
    nome_produto = serializers.CharField()
    quantidade = serializers.IntegerField()
    observacoes_item = serializers.CharField(allow_null=True, required=False)

    # This serializer is for representation only, no create/update needed here.
    # Data comes from ItemPedidoMesa or formatted from PedidoWhatsApp.carrinho_atual

# Serializer for the consolidated list of orders for the kitchen
class ConsolidatedPedidoCozinhaSerializer(serializers.Serializer):
    id_pedido_origem = serializers.IntegerField()
    tipo_origem = serializers.CharField() # "WhatsApp" ou "Mesa"
    identificador_cliente = serializers.CharField() # Número da Mesa ou Telefone/Nome do Cliente WhatsApp
    horario_entrada_cozinha = serializers.DateTimeField()
    status_cozinha_atual = serializers.CharField()
    itens = ItemConsolidadoSerializer(many=True)
    # total_itens = serializers.IntegerField() # Pode ser útil para a cozinha

    # This serializer is for representation only.

# Serializer for the payload to update kitchen status
class KitchenStatusUpdateSerializer(serializers.Serializer):
    # Define choices based on a common set or allow any valid string for now,
    # validation will happen in the view against model choices.
    # Using the choices from one of the models as a reference.
    STATUS_CHOICES = PedidoMesa.STATUS_COZINHA_CHOICES # Or PedidoWhatsApp.STATUS_COZINHA_CHOICES
    
    status_cozinha = serializers.ChoiceField(choices=STATUS_CHOICES)

    def validate_status_cozinha(self, value):
        # Allow only 'EmPreparo' or 'Pronto' for this specific endpoint
        if value not in [PedidoMesa.STATUS_COZINHA_EM_PREPARO, PedidoMesa.STATUS_COZINHA_PRONTO]:
            raise serializers.ValidationError(f"Status inválido. Apenas '{PedidoMesa.STATUS_COZINHA_EM_PREPARO}' ou '{PedidoMesa.STATUS_COZINHA_PRONTO}' são permitidos aqui.")
        return value
