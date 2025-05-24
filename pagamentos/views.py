from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.contenttypes.models import ContentType

from .models import Pagamento
from .serializers import PagamentoSerializer
# Importar os modelos de pedido para verificar se o tipo de origem é válido
from whatsapp_bot.models import PedidoWhatsApp
from atendimento_interno.models import PedidoMesa


class ListarPagamentosPorPedidoView(ListAPIView):
    """
    Lista todos os pagamentos associados a um pedido específico.
    URL: /api/pagamentos/pedido/{tipo_origem}/{id_pedido_origem}/
    """
    serializer_class = PagamentoSerializer

    def get_queryset(self):
        tipo_origem = self.kwargs.get('tipo_origem', '').lower()
        id_pedido_origem = self.kwargs.get('id_pedido_origem')

        if not tipo_origem or not id_pedido_origem:
            return Pagamento.objects.none() # Retorna queryset vazio se parâmetros faltando

        model_map = {
            'whatsapp': PedidoWhatsApp,
            'mesa': PedidoMesa,
        }

        model_class = model_map.get(tipo_origem)
        if not model_class:
            # Em uma API real, você poderia levantar um Http404 ou erro de validação aqui.
            # Para ListAPIView, retornar um queryset vazio é seguro se os parâmetros são inválidos.
            return Pagamento.objects.none()

        try:
            # Validar se o id_pedido_origem é um inteiro
            id_pedido_origem_int = int(id_pedido_origem)
            # Validar se o pedido original existe (opcional, mas bom para evitar lixo)
            # model_class.objects.get(id=id_pedido_origem_int) # Isso pode ser pesado se chamado sempre
        except (ValueError, model_class.DoesNotExist):
            return Pagamento.objects.none()
        
        content_type = ContentType.objects.get_for_model(model_class)
        return Pagamento.objects.filter(
            content_type=content_type,
            object_id=id_pedido_origem_int
        ).order_by('-data_hora_pagamento')

    def list(self, request, *args, **kwargs):
        # Adicionar validação explícita dos parâmetros da URL e retornar 400/404 se necessário.
        tipo_origem = self.kwargs.get('tipo_origem', '').lower()
        id_pedido_origem_str = self.kwargs.get('id_pedido_origem')

        if not tipo_origem or not id_pedido_origem_str:
            return Response(
                {"detail": "Parâmetros 'tipo_origem' e 'id_pedido_origem' são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        model_map = {
            'whatsapp': PedidoWhatsApp,
            'mesa': PedidoMesa,
        }
        model_class = model_map.get(tipo_origem)
        if not model_class:
            return Response(
                {"detail": f"Tipo de origem '{tipo_origem}' inválido. Use 'whatsapp' ou 'mesa'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            id_pedido_origem = int(id_pedido_origem_str)
            # Opcional: verificar se o pedido pai realmente existe
            # get_object_or_404(model_class, id=id_pedido_origem)
        except ValueError:
            return Response(
                {"detail": "ID do pedido deve ser um número inteiro."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset()
        if not queryset.exists() and id_pedido_origem_str: # Se o ID foi fornecido mas nada encontrado
            # Verificar se o pedido pai existe para dar um 404 mais preciso ou apenas lista vazia
            try:
                ContentType.objects.get_for_model(model_class).get_object_for_this_type(id=id_pedido_origem)
                # Pedido pai existe, mas não tem pagamentos. Retorna lista vazia (comportamento padrão do ListAPIView).
            except model_class.DoesNotExist:
                 return Response(
                    {"detail": f"Pedido com ID {id_pedido_origem} do tipo '{tipo_origem}' não encontrado."},
                    status=status.HTTP_404_NOT_FOUND
                )


        return super().list(request, *args, **kwargs)

# Outras views para pagamentos (ex: criar, atualizar status de pagamento)
# podem ser adicionadas aqui se o app 'pagamentos' for responsável por mais do que apenas listar.
# No MVP atual, a criação é feita via o serviço chamado pelos apps de pedido.
# Atualizações de status de pagamento (ex: de Pendente para Aprovado via webhook de gateway)
# seriam Pós-MVP e poderiam ter suas próprias views aqui.
