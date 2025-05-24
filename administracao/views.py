from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from django.db.models import Sum, Count, Q, F
from django.utils.dateparse import parse_datetime, parse_date
from django.contrib.contenttypes.models import ContentType

from .models import ConfiguracaoSistema, ProdutoPlaceholder, CategoriaProdutoPlaceholder
from .serializers import (
    ConfiguracaoSistemaSerializer, ProdutoPlaceholderSerializer, CategoriaProdutoPlaceholderSerializer,
    MesaAdminSerializer, VendasSimplesRelatorioSerializer, ProdutosVendidosSimplesRelatorioSerializer
)
from atendimento_interno.models import Mesa, ItemPedidoMesa, PedidoMesa
from pagamentos.models import Pagamento
from whatsapp_bot.models import PedidoWhatsApp # For product sales report

# --- Gerenciamento de Cardápio (using Placeholders) ---
class CategoriaProdutoAdminViewSet(viewsets.ModelViewSet):
    """
    API para CRUD de Categorias de Produtos (Admin).
    """
    queryset = CategoriaProdutoPlaceholder.objects.all().order_by('nome')
    serializer_class = CategoriaProdutoPlaceholderSerializer
    # TODO: Adicionar permissões (ex: IsAdminUser)

class ProdutoAdminViewSet(viewsets.ModelViewSet):
    """
    API para CRUD de Produtos (Admin).
    """
    queryset = ProdutoPlaceholder.objects.all().order_by('nome')
    serializer_class = ProdutoPlaceholderSerializer
    # TODO: Adicionar permissões
    # TODO: Lidar com upload de foto se necessário (Pós-MVP ou via campo URL no serializer)

# --- Gerenciamento de Mesas ---
class MesaAdminViewSet(viewsets.ModelViewSet):
    """
    API para CRUD de Mesas (Admin).
    O controle operacional de status da mesa é feito pelo app atendimento_interno.
    Este endpoint é para configuração das mesas.
    """
    queryset = Mesa.objects.all().order_by('numero_identificador')
    serializer_class = MesaAdminSerializer
    # TODO: Adicionar permissões

# --- Configurações Gerais do Sistema ---
class ConfiguracaoSistemaViewSet(viewsets.ModelViewSet):
    """
    API para CRUD de Configurações do Sistema (Admin).
    A criação (POST) e deleção (DELETE) de chaves pode ser restrita ou desabilitada
    se as chaves forem fixas e apenas valores devem ser editados.
    Por padrão, ModelViewSet permite tudo.
    """
    queryset = ConfiguracaoSistema.objects.all().order_by('chave')
    serializer_class = ConfiguracaoSistemaSerializer
    lookup_field = 'chave' # Usar 'chave' em vez de 'id' na URL
    # TODO: Adicionar permissões

    # Desabilitar POST e DELETE se as chaves são predefinidas e não devem ser criadas/removidas via API
    # def create(self, request, *args, **kwargs):
    #     return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    # def destroy(self, request, *args, **kwargs):
    #     return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


# --- Relatórios ---
class VendasSimplesRelatorioView(generics.ListAPIView):
    """
    API para Relatório de Vendas Simples.
    Filtros via query params: data_inicio, data_fim (formato YYYY-MM-DD)
    Ex: /api/admin/relatorios/vendas_simples/?data_inicio=2023-01-01&data_fim=2023-01-31
    """
    serializer_class = VendasSimplesRelatorioSerializer
    # TODO: Adicionar permissões

    def get_queryset(self):
        queryset = Pagamento.objects.filter(status_pagamento=Pagamento.STATUS_APROVADO)
        
        data_inicio_str = self.request.query_params.get('data_inicio')
        data_fim_str = self.request.query_params.get('data_fim')

        if data_inicio_str:
            data_inicio = parse_date(data_inicio_str)
            if data_inicio:
                queryset = queryset.filter(data_hora_pagamento__gte=data_inicio)
        
        if data_fim_str:
            data_fim = parse_date(data_fim_str)
            if data_fim:
                # Adicionar 1 dia ao data_fim para incluir todos os horários do dia final
                from datetime import timedelta
                data_fim_ajustada = data_fim + timedelta(days=1)
                queryset = queryset.filter(data_hora_pagamento__lt=data_fim_ajustada)
                
        return queryset.order_by('-data_hora_pagamento')


class ProdutosVendidosSimplesRelatorioView(APIView):
    """
    API para Relatório de Produtos Vendidos Simples.
    Filtros via query params: data_inicio, data_fim (formato YYYY-MM-DD)
    Ex: /api/admin/relatorios/produtos_vendidos_simples/?data_inicio=2023-01-01&data_fim=2023-01-31
    """
    # TODO: Adicionar permissões

    def get(self, request, *args, **kwargs):
        data_inicio_str = self.request.query_params.get('data_inicio')
        data_fim_str = self.request.query_params.get('data_fim')

        # --- Vendas de Pedidos de Mesa ---
        itens_mesa_qs = ItemPedidoMesa.objects.filter(
            pedido_mesa__status_pedido=PedidoMesa.STATUS_PAGO # Considera apenas pedidos pagos
        )
        if data_inicio_str:
            data_inicio = parse_date(data_inicio_str)
            if data_inicio:
                itens_mesa_qs = itens_mesa_qs.filter(pedido_mesa__data_fechamento__gte=data_inicio)
        if data_fim_str:
            data_fim = parse_date(data_fim_str)
            if data_fim:
                from datetime import timedelta
                data_fim_ajustada = data_fim + timedelta(days=1)
                itens_mesa_qs = itens_mesa_qs.filter(pedido_mesa__data_fechamento__lt=data_fim_ajustada)
        
        # Agregação para itens de mesa
        # Usando o ProdutoPlaceholder. Se fosse Produto real, seria produto__nome.
        # Como ItemPedidoMesa tem FK para Produto (placeholder ou real), podemos usar produto__nome.
        # Se ProdutoPlaceholder está em administracao.models e ItemPedidoMesa.produto aponta para ele:
        vendas_mesa_agregado = list(itens_mesa_qs
            .values('produto__nome') # Assumindo que ItemPedidoMesa.produto é FK para ProdutoPlaceholder
            .annotate(quantidade_total_vendida=Sum('quantidade'))
            .filter(quantidade_total_vendida__gt=0) # Apenas se houve vendas
            .order_by('-quantidade_total_vendida', 'produto__nome')
        )
        # Renomear 'produto__nome' para 'nome_produto' para corresponder ao serializer
        for item in vendas_mesa_agregado:
            item['nome_produto'] = item.pop('produto__nome')


        # --- Vendas de Pedidos WhatsApp ---
        # Acessar carrinho_atual (JSONField) de PedidoWhatsApp.
        # Filtrar PedidoWhatsApp que foram pagos (status_pagamento='Aprovado' no modelo Pagamento associado)
        content_type_whatsapp = ContentType.objects.get_for_model(PedidoWhatsApp)
        pagamentos_whatsapp_aprovados_ids = Pagamento.objects.filter(
            content_type=content_type_whatsapp,
            status_pagamento=Pagamento.STATUS_APROVADO
        ).values_list('object_id', flat=True)

        pedidos_whatsapp_pagos_qs = PedidoWhatsApp.objects.filter(id__in=pagamentos_whatsapp_aprovados_ids)

        if data_inicio_str:
            data_inicio = parse_date(data_inicio_str)
            if data_inicio:
                # Filtrar por data de atualização do PedidoWhatsApp ou data do pagamento associado
                # Usar data do pagamento é mais preciso
                pagamentos_whatsapp_aprovados_ids_data_filtrada = Pagamento.objects.filter(
                    content_type=content_type_whatsapp,
                    status_pagamento=Pagamento.STATUS_APROVADO,
                    data_hora_pagamento__gte=data_inicio
                ).values_list('object_id', flat=True)
                pedidos_whatsapp_pagos_qs = pedidos_whatsapp_pagos_qs.filter(id__in=pagamentos_whatsapp_aprovados_ids_data_filtrada)

        if data_fim_str:
            data_fim = parse_date(data_fim_str)
            if data_fim:
                from datetime import timedelta
                data_fim_ajustada = data_fim + timedelta(days=1)
                pagamentos_whatsapp_aprovados_ids_data_filtrada_fim = Pagamento.objects.filter(
                    content_type=content_type_whatsapp,
                    status_pagamento=Pagamento.STATUS_APROVADO,
                    data_hora_pagamento__lt=data_fim_ajustada
                ).values_list('object_id', flat=True)
                # Interseção com o filtro de data_inicio se ambos estiverem presentes
                if data_inicio_str and data_inicio:
                    final_ids = set(pagamentos_whatsapp_aprovados_ids_data_filtrada).intersection(set(pagamentos_whatsapp_aprovados_ids_data_filtrada_fim))
                    pedidos_whatsapp_pagos_qs = PedidoWhatsApp.objects.filter(id__in=list(final_ids))
                else:
                    pedidos_whatsapp_pagos_qs = pedidos_whatsapp_pagos_qs.filter(id__in=pagamentos_whatsapp_aprovados_ids_data_filtrada_fim)


        vendas_whatsapp_dict = {} # { 'nome_produto': quantidade }
        for pedido_wp in pedidos_whatsapp_pagos_qs:
            if isinstance(pedido_wp.carrinho_atual, list):
                for item_carrinho in pedido_wp.carrinho_atual:
                    nome_produto = item_carrinho.get('nome')
                    quantidade = item_carrinho.get('quantidade', 0)
                    if nome_produto and quantidade > 0:
                        vendas_whatsapp_dict[nome_produto] = vendas_whatsapp_dict.get(nome_produto, 0) + quantidade
        
        # Combinar resultados de Mesa e WhatsApp
        resultado_combinado_dict = {}
        for item_mesa in vendas_mesa_agregado:
            nome = item_mesa['nome_produto']
            qtd = item_mesa['quantidade_total_vendida']
            resultado_combinado_dict[nome] = resultado_combinado_dict.get(nome, 0) + qtd
        
        for nome_produto, qtd in vendas_whatsapp_dict.items():
            resultado_combinado_dict[nome_produto] = resultado_combinado_dict.get(nome_produto, 0) + qtd

        # Converter para o formato do serializer
        resultado_final_lista = []
        for nome, qtd_total in resultado_combinado_dict.items():
            resultado_final_lista.append({'nome_produto': nome, 'quantidade_total_vendida': qtd_total})
        
        # Ordenar
        resultado_final_lista.sort(key=lambda x: (-x['quantidade_total_vendida'], x['nome_produto']))

        serializer = ProdutosVendidosSimplesRelatorioSerializer(resultado_final_lista, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
