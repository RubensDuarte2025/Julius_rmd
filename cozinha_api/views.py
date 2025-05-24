from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Q

from whatsapp_bot.models import PedidoWhatsApp
from atendimento_interno.models import PedidoMesa, ItemPedidoMesa
from .serializers import ConsolidatedPedidoCozinhaSerializer, KitchenStatusUpdateSerializer, ItemConsolidadoSerializer

class PedidosParaPrepararListView(APIView):
    """
    Lista todos os PedidoWhatsApp e PedidoMesa que estão com
    status_cozinha = 'AguardandoPreparo' ou 'EmPreparo'.
    Ordena por horario_entrada_cozinha (mais antigos primeiro).
    """
    def get(self, request, *args, **kwargs):
        pedidos_whatsapp = PedidoWhatsApp.objects.filter(
            Q(status_cozinha=PedidoWhatsApp.STATUS_COZINHA_AGUARDANDO) |
            Q(status_cozinha=PedidoWhatsApp.STATUS_COZINHA_EM_PREPARO)
        ).exclude(status_cozinha__isnull=True).exclude(status_cozinha='').order_by('horario_entrada_cozinha')

        pedidos_mesa = PedidoMesa.objects.filter(
            Q(status_cozinha=PedidoMesa.STATUS_COZINHA_AGUARDANDO) |
            Q(status_cozinha=PedidoMesa.STATUS_COZINHA_EM_PREPARO)
        ).exclude(status_cozinha__isnull=True).exclude(status_cozinha='').order_by('horario_entrada_cozinha')

        pedidos_consolidados = []

        # Processar Pedidos WhatsApp
        for pw in pedidos_whatsapp:
            itens_formatados = []
            if isinstance(pw.carrinho_atual, list): # carrinho_atual is a list of dicts
                for item_no_carrinho in pw.carrinho_atual:
                    itens_formatados.append(ItemConsolidadoSerializer({
                        'nome_produto': item_no_carrinho.get('nome', 'Produto Desconhecido'),
                        'quantidade': item_no_carrinho.get('quantidade', 0),
                        'observacoes_item': item_no_carrinho.get('observacoes', '') # Assumindo que pode haver 'observacoes' no item do carrinho
                    }).data)
            
            pedidos_consolidados.append({
                'id_pedido_origem': pw.id,
                'tipo_origem': 'WhatsApp',
                'identificador_cliente': pw.nome_cliente or pw.telefone_cliente,
                'horario_entrada_cozinha': pw.horario_entrada_cozinha,
                'status_cozinha_atual': pw.status_cozinha,
                'itens': itens_formatados,
            })

        # Processar Pedidos de Mesa
        for pm in pedidos_mesa:
            itens_formatados = []
            for item_pedido_mesa in pm.itens_pedido.all(): # itens_pedido is a related manager
                itens_formatados.append(ItemConsolidadoSerializer({
                    'nome_produto': item_pedido_mesa.produto.nome, # Assumindo que produto.nome existe
                    'quantidade': item_pedido_mesa.quantidade,
                    'observacoes_item': item_pedido_mesa.observacoes_item
                }).data)

            pedidos_consolidados.append({
                'id_pedido_origem': pm.id,
                'tipo_origem': 'Mesa',
                'identificador_cliente': f"Mesa {pm.mesa.numero_identificador}",
                'horario_entrada_cozinha': pm.horario_entrada_cozinha,
                'status_cozinha_atual': pm.status_cozinha,
                'itens': itens_formatados,
            })
        
        # Ordenar a lista consolidada por horario_entrada_cozinha
        # Pedidos sem horário de entrada (improvável dado o filtro, mas por segurança) viriam por último ou primeiro dependendo do None handling
        pedidos_consolidados.sort(key=lambda p: p['horario_entrada_cozinha'] or timezone.now())

        serializer = ConsolidatedPedidoCozinhaSerializer(pedidos_consolidados, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AtualizarStatusCozinhaView(APIView):
    """
    Atualiza o status_cozinha de um pedido específico (WhatsApp ou Mesa).
    PATCH /api/cozinha/pedidos/{tipo_origem}/{id_pedido_origem}/status/
    Input: { "status_cozinha": "EmPreparo" } ou { "status_cozinha": "Pronto" }.
    """
    def patch(self, request, tipo_origem, id_pedido_origem, *args, **kwargs):
        serializer = KitchenStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        novo_status_cozinha = serializer.validated_data['status_cozinha']
        pedido_obj = None
        
        try:
            id_pedido_origem = int(id_pedido_origem)
        except ValueError:
            return Response({'detail': 'ID do pedido inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        if tipo_origem.lower() == 'whatsapp':
            try:
                pedido_obj = PedidoWhatsApp.objects.get(id=id_pedido_origem)
            except PedidoWhatsApp.DoesNotExist:
                return Response({'detail': 'Pedido WhatsApp não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        elif tipo_origem.lower() == 'mesa':
            try:
                pedido_obj = PedidoMesa.objects.get(id=id_pedido_origem)
            except PedidoMesa.DoesNotExist:
                return Response({'detail': 'Pedido de Mesa não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'detail': 'Tipo de origem inválido. Use "whatsapp" ou "mesa".'}, status=status.HTTP_400_BAD_REQUEST)

        if not pedido_obj.status_cozinha:
             return Response({'detail': f'Este pedido ainda não foi enviado para a cozinha.'}, status=status.HTTP_400_BAD_REQUEST)

        # Lógica de transição de status (exemplo simples)
        # (AguardandoPreparo -> EmPreparo), (EmPreparo -> Pronto)
        if pedido_obj.status_cozinha == PedidoWhatsApp.STATUS_COZINHA_AGUARDANDO and novo_status_cozinha != PedidoWhatsApp.STATUS_COZINHA_EM_PREPARO:
            return Response({'detail': f'Status inválido. Pedido "Aguardando Preparo" só pode ir para "Em Preparo".'}, status=status.HTTP_400_BAD_REQUEST)
        if pedido_obj.status_cozinha == PedidoWhatsApp.STATUS_COZINHA_EM_PREPARO and novo_status_cozinha != PedidoWhatsApp.STATUS_COZINHA_PRONTO:
            return Response({'detail': f'Status inválido. Pedido "Em Preparo" só pode ir para "Pronto".'}, status=status.HTTP_400_BAD_REQUEST)
        if pedido_obj.status_cozinha == PedidoWhatsApp.STATUS_COZINHA_PRONTO: # Já está pronto, não deveria mudar por esta API
             return Response({'detail': f'Pedido já está "Pronto". Nenhuma alteração permitida por esta API.'}, status=status.HTTP_400_BAD_REQUEST)


        pedido_obj.status_cozinha = novo_status_cozinha
        
        # Se estiver indo para "Pronto", poderia registrar um horário de finalização, se houvesse tal campo.
        # if novo_status_cozinha == PedidoWhatsApp.STATUS_COZINHA_PRONTO:
        #     pedido_obj.horario_finalizacao_cozinha = timezone.now() # Exemplo, se campo existir

        pedido_obj.save()

        # Retornar o pedido atualizado no formato consolidado pode ser uma boa prática,
        # mas para simplificar, apenas um success com o novo status.
        return Response({
            'id_pedido_origem': pedido_obj.id,
            'tipo_origem': tipo_origem.lower(),
            'status_cozinha_novo': novo_status_cozinha
        }, status=status.HTTP_200_OK)
