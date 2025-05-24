from rest_framework import serializers
from .models import ConfiguracaoSistema, ProdutoPlaceholder, CategoriaProdutoPlaceholder
from atendimento_interno.models import Mesa # For MesaAdminSerializer
from pagamentos.models import Pagamento # For VendasSimplesRelatorio
from atendimento_interno.models import ItemPedidoMesa # For ProdutosVendidos
from whatsapp_bot.models import PedidoWhatsApp # For ProdutosVendidos from WhatsApp

# --- Cardápio Serializers (using Placeholders) ---
class CategoriaProdutoPlaceholderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaProdutoPlaceholder
        fields = ['id', 'nome', 'descricao']

class ProdutoPlaceholderSerializer(serializers.ModelSerializer):
    # If CategoriaProdutoPlaceholderSerializer is used for nested representation:
    # categoria = CategoriaProdutoPlaceholderSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=CategoriaProdutoPlaceholder.objects.all(),
        source='categoria',
        allow_null=True # Based on model allowing null category
    )
    # To show category name on read, and allow ID on write:
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True, allow_null=True)


    class Meta:
        model = ProdutoPlaceholder
        fields = [
            'id', 'nome', 'descricao', 'preco_base', 'disponivel', 
            'categoria_id', 'categoria_nome', 'ingredientes_base', 'foto_url'
        ]

# --- Mesa Admin Serializer ---
class MesaAdminSerializer(serializers.ModelSerializer):
    # This serializer is for the admin CRUD API. It might be similar to MesaSerializer
    # in atendimento_interno, but can be tailored for admin purposes if needed.
    class Meta:
        model = Mesa
        fields = ['id', 'numero_identificador', 'capacidade_default', 'status']
        # For admin, 'status' might be read-only if it's purely operational,
        # or updatable if admin can override/interdict tables.
        # The 'status' field on Mesa model has choices, DRF handles this well.

# --- Configuração Sistema Serializer ---
class ConfiguracaoSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracaoSistema
        fields = ['chave', 'valor', 'descricao']
        read_only_fields = ['chave'] # Chave is the identifier, usually not changed after creation.

# --- Relatórios Serializers ---
class VendasSimplesRelatorioSerializer(serializers.Serializer):
    # Based on Pagamento model, but can be adapted.
    # Formato: { "id_pedido", "data_pagamento", "valor_pago", "metodo_pagamento", "origem_pedido" (WhatsApp/Mesa) }
    # This implies we are serializing Pagamento objects directly or constructing these dicts.
    
    id_pagamento = serializers.IntegerField(source='id') # Assuming we serialize Pagamento objects
    # id_pedido is object_id from Pagamento model
    id_pedido_origem = serializers.IntegerField(source='object_id')
    data_pagamento = serializers.DateTimeField(source='data_hora_pagamento')
    valor_pago = serializers.DecimalField(max_digits=10, decimal_places=2)
    metodo_pagamento = serializers.CharField(source='get_metodo_pagamento_display') # Display value
    
    # origem_pedido needs custom logic based on content_type
    origem_pedido = serializers.SerializerMethodField()

    def get_origem_pedido(self, obj):
        # obj is a Pagamento instance
        if obj.content_type:
            model_name = obj.content_type.model
            if model_name == 'pedidowhatsapp':
                return 'WhatsApp'
            elif model_name == 'pedidomesa':
                return 'Mesa'
        return 'Desconhecida'

    class Meta:
        # This serializer isn't strictly a ModelSerializer if we are constructing dicts.
        # If we serialize Pagamento objects directly and add custom fields, it's fine.
        model = Pagamento # Assuming we are selecting Pagamento objects
        fields = ['id_pagamento', 'id_pedido_origem', 'data_pagamento', 'valor_pago', 'metodo_pagamento', 'origem_pedido']


class ProdutosVendidosSimplesRelatorioSerializer(serializers.Serializer):
    # Formato: { "nome_produto", "quantidade_total_vendida" }
    # This serializer represents an aggregated result, not a direct model.
    nome_produto = serializers.CharField()
    quantidade_total_vendida = serializers.IntegerField()
