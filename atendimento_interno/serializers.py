from rest_framework import serializers
# from products.models import Produto # Assuming a real Product model from a 'products' app
# from products.serializers import ProdutoSerializer # Assuming a ProductSerializer exists
from .models import Mesa, PedidoMesa, ItemPedidoMesa, Produto # Using the placeholder Produto for now

# Placeholder for ProdutoSerializer if not available from a 'products' app
class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ['id', 'nome', 'preco_base']


class ItemPedidoMesaSerializer(serializers.ModelSerializer):
    produto_id = serializers.PrimaryKeyRelatedField(
        queryset=Produto.objects.all(), source='produto', write_only=True
    )
    produto = ProdutoSerializer(read_only=True) # Nested for readable output

    class Meta:
        model = ItemPedidoMesa
        fields = [
            'id', 'pedido_mesa', 'produto_id', 'produto', 'quantidade',
            'preco_unitario_no_momento', 'subtotal_item', 'observacoes_item'
        ]
        read_only_fields = ['pedido_mesa', 'subtotal_item'] # pedido_mesa is set by view, subtotal is calculated

    def validate(self, data):
        # Ensure preco_unitario_no_momento is set if a product is being added
        # For updates, it might not be present if only quantity changes, but it should have been set initially.
        if 'produto' in data and data.get('preco_unitario_no_momento') is None:
            produto_obj = data['produto']
            data['preco_unitario_no_momento'] = produto_obj.preco_base
        return data

    def create(self, validated_data):
        # Ensure subtotal is calculated based on validated price and quantity
        produto = validated_data['produto']
        quantidade = validated_data['quantidade']
        
        # If preco_unitario_no_momento is not provided, fetch from product.
        # This is also handled in validate, but good to be defensive.
        preco_unitario = validated_data.get('preco_unitario_no_momento', produto.preco_base)
        validated_data['preco_unitario_no_momento'] = preco_unitario
        validated_data['subtotal_item'] = quantidade * preco_unitario
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Recalculate subtotal if quantity or price changes
        instance.quantidade = validated_data.get('quantidade', instance.quantidade)
        # Allowing price update here might be complex; usually, price is fixed at add time.
        # If price_unitario_no_momento is part of validated_data, it means it's being explicitly changed.
        instance.preco_unitario_no_momento = validated_data.get('preco_unitario_no_momento', instance.preco_unitario_no_momento)
        instance.subtotal_item = instance.quantidade * instance.preco_unitario_no_momento
        
        # Update other fields
        instance.observacoes_item = validated_data.get('observacoes_item', instance.observacoes_item)
        instance.save()
        return instance


class PedidoMesaSerializer(serializers.ModelSerializer):
    itens_pedido = ItemPedidoMesaSerializer(many=True, read_only=True)
    total_pedido = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True, source='calcular_total')
    mesa_numero = serializers.CharField(source='mesa.numero_identificador', read_only=True)

    class Meta:
        model = PedidoMesa
        fields = [
            'id', 'mesa', 'mesa_numero', 'status_pedido', 'data_abertura', 'data_fechamento',
            'observacoes_gerais', 'itens_pedido', 'total_pedido',
            'metodo_pagamento_registrado', 'valor_pago_registrado' # For MVP payment registration
        ]
        read_only_fields = ['data_abertura', 'data_fechamento', 'total_pedido']

    # For creating/updating orders, items might be handled by their own dedicated endpoints
    # or by accepting nested writes (more complex, often avoided for simplicity).
    # For MVP, adding items will be via /api/pedidos_mesa/{pedido_id}/itens/


class MesaSerializer(serializers.ModelSerializer):
    # Optionally, include active orders or summary
    # pedidos_ativos = PedidoMesaSerializer(many=True, read_only=True, source='pedidos') # Example if filtering for active
    
    # For MVP, a simpler representation might be fine.
    # If including pedidos, filter for 'Aberto' or 'Fechado' (not 'Pago' or 'Cancelado')
    pedidos_recentes = serializers.SerializerMethodField()

    class Meta:
        model = Mesa
        fields = ['id', 'numero_identificador', 'status', 'capacidade_default', 'pedidos_recentes']

    def get_pedidos_recentes(self, obj):
        # Get pedidos that are not 'Pago' or 'Cancelado'
        pedidos_filtrados = obj.pedidos.exclude(status_pedido__in=[PedidoMesa.STATUS_PAGO, PedidoMesa.STATUS_CANCELADO])
        serializer = PedidoMesaSerializer(pedidos_filtrados, many=True, context=self.context)
        return serializer.data


class MesaStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = ['status']


class PedidoMesaUpdateSerializer(serializers.ModelSerializer):
    # For general updates like observations or changing status (e.g., to 'Fechado')
    class Meta:
        model = PedidoMesa
        fields = ['observacoes_gerais', 'status_pedido']
        # Mesa and items are not directly updatable through this specific serializer


from pagamentos.models import Pagamento as PagamentoModel # Import Pagamento model

class PagamentoRegistroSerializer(serializers.Serializer):
    # Usar os choices definidos no modelo Pagamento para consistência.
    # No entanto, o frontend do atendimento interno pode querer apresentar um subconjunto.
    # Para MVP, o atendente registra o que foi usado.
    # O PedidoMesa.METODO_PAGAMENTO_CHOICES é ('dinheiro', 'cartao_maquineta', 'pix_maquineta')
    # O Pagamento.METODO_PAGAMENTO_CHOICES é mais abrangente.
    # Para o registro manual pelo atendente, as opções do PedidoMesa são suficientes
    # e o serviço de pagamento pode mapeá-los se necessário.
    # Vamos manter os choices do PedidoMesa por enquanto, pois reflete o que o atendente registra.
    # A view já está preparada para mapear 'cartao_maquineta' se preciso.
    # Se a intenção é que o atendente escolha entre TODOS os métodos de Pagamento, então sim, mudaríamos.
    # Mas a descrição da API do atendimento_interno é para métodos manuais.
    # Para consistência, o ideal seria que PagamentoRegistroSerializer tivesse os mesmos choices do Modelo Pagamento
    # e o frontend do atendente filtraria os que fazem sentido.
    # Vamos alinhar com o modelo Pagamento para maior flexibilidade futura.
    
    # Filtrar os choices do PagamentoModel para apenas os que fazem sentido para registro manual pelo atendente
    MANUAL_PAYMENT_METHODS = [
        (PagamentoModel.METODO_DINHEIRO, 'Dinheiro'),
        (PagamentoModel.METODO_CARTAO_DEBITO_MAQUINETA, 'Cartão de Débito (Maquineta)'),
        (PagamentoModel.METODO_CARTAO_CREDITO_MAQUINETA, 'Cartão de Crédito (Maquineta)'),
        (PagamentoModel.METODO_PIX, 'PIX (Maquineta/QR Fixo)'), # Assumindo PIX manual
        (PagamentoModel.METODO_OUTRO, 'Outro'),
    ]
    metodo = serializers.ChoiceField(choices=MANUAL_PAYMENT_METHODS)
    valor_pago = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_valor_pago(self, value):
        if value <= 0:
            raise serializers.ValidationError("O valor pago deve ser positivo.")
        return value
