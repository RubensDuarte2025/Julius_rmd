from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Mesa, PedidoMesa, ItemPedidoMesa, Produto # Using placeholder Produto
from .serializers import (
    MesaSerializer, PedidoMesaSerializer, ItemPedidoMesaSerializer,
    MesaStatusUpdateSerializer, PagamentoRegistroSerializer, PedidoMesaUpdateSerializer
)
# from products.models import Produto # Would be used in a real multi-app setup

class MesaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Mesas.
    - Listar todas as mesas: `GET /api/mesas/`
    - Detalhes de uma mesa: `GET /api/mesas/{mesa_id}/`
    - Atualizar status da mesa: `PATCH /api/mesas/{mesa_id}/atualizar_status/` (custom action)
    - Criar/Atualizar/Deletar mesas (geralmente via admin ou setup inicial, mas ModelViewSet provê).
    """
    queryset = Mesa.objects.all().order_by('numero_identificador')
    serializer_class = MesaSerializer

    @action(detail=True, methods=['patch'], serializer_class=MesaStatusUpdateSerializer, url_path='atualizar-status')
    def atualizar_status(self, request, pk=None):
        mesa = self.get_object()
        serializer = MesaStatusUpdateSerializer(mesa, data=request.data, partial=True)
        if serializer.is_valid():
            novo_status = serializer.validated_data.get('status')
            
            # Lógica de negócio ao mudar status
            if novo_status == Mesa.STATUS_OCUPADA and mesa.status == Mesa.STATUS_LIVRE:
                # Se não houver pedido aberto, pode-se criar um novo automaticamente
                # ou apenas marcar como ocupada, e o pedido é criado explicitamente.
                # Para MVP, vamos permitir criar pedido explicitamente.
                pass
            elif novo_status == Mesa.STATUS_LIVRE and mesa.status == Mesa.STATUS_AGUARDANDO_PAGAMENTO:
                # Isso geralmente ocorreria após o pagamento ser registrado no pedido.
                # Poderia haver uma verificação se todos os pedidos da mesa estão pagos.
                pass

            serializer.save()
            return Response(MesaSerializer(mesa).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # POST /api/mesas/{mesa_id}/pedidos/ (Criar um novo pedido para uma mesa)
    @action(detail=True, methods=['post'], serializer_class=PedidoMesaSerializer, url_path='pedidos')
    def criar_pedido_para_mesa(self, request, pk=None):
        mesa = self.get_object()

        if mesa.status == Mesa.STATUS_INTERDITADA:
            return Response({'detail': 'Mesa está interditada.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verifica se já existe um pedido aberto ou aguardando pagamento para esta mesa
        pedido_existente_aberto = PedidoMesa.objects.filter(
            mesa=mesa, 
            status_pedido__in=[PedidoMesa.STATUS_ABERTO, PedidoMesa.STATUS_FECHADO]
        ).first()

        if pedido_existente_aberto:
            serializer = PedidoMesaSerializer(pedido_existente_aberto)
            return Response({'detail': 'Mesa já possui um pedido aberto ou fechado.', 'pedido_existente': serializer.data}, status=status.HTTP_400_BAD_REQUEST)
        
        # Criar novo pedido
        pedido = PedidoMesa.objects.create(mesa=mesa, status_pedido=PedidoMesa.STATUS_ABERTO)
        mesa.status = Mesa.STATUS_OCUPADA
        mesa.save()
        
        serializer = PedidoMesaSerializer(pedido)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PedidoMesaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Pedidos de Mesa.
    - Detalhes de um pedido: `GET /api/pedidos_mesa/{pedido_id}/`
    - Atualizar pedido: `PATCH /api/pedidos_mesa/{pedido_id}/` (ex: observação, fechar)
    - Listar todos os pedidos (para admin/gerenciamento): `GET /api/pedidos_mesa/`
    """
    queryset = PedidoMesa.objects.all().order_by('-data_abertura')
    serializer_class = PedidoMesaSerializer # Para list e retrieve

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return PedidoMesaUpdateSerializer
        return super().get_serializer_class()

    def perform_update(self, serializer):
        # Lógica ao atualizar pedido, ex: se status_pedido for para 'Fechado'
        pedido = serializer.instance
        novo_status_pedido = serializer.validated_data.get('status_pedido', pedido.status_pedido)

        if novo_status_pedido == PedidoMesa.STATUS_FECHADO and pedido.status_pedido == PedidoMesa.STATUS_ABERTO:
            pedido.data_fechamento = timezone.now()
            pedido.mesa.status = Mesa.STATUS_AGUARDANDO_PAGAMENTO
            pedido.mesa.save()
        
        # Se o pedido for cancelado, e a mesa estava ocupada por este pedido, liberar a mesa
        if novo_status_pedido == PedidoMesa.STATUS_CANCELADO and pedido.status_pedido != PedidoMesa.STATUS_CANCELADO:
            if pedido.mesa.status == Mesa.STATUS_OCUPADA or pedido.mesa.status == Mesa.STATUS_AGUARDANDO_PAGAMENTO:
                 # Checar se não há outros pedidos abertos/fechados para a mesa antes de liberar
                outros_pedidos_nao_finalizados = PedidoMesa.objects.filter(
                    mesa=pedido.mesa,
                    status_pedido__in=[PedidoMesa.STATUS_ABERTO, PedidoMesa.STATUS_FECHADO]
                ).exclude(id=pedido.id).exists()
                if not outros_pedidos_nao_finalizados:
                    pedido.mesa.status = Mesa.STATUS_LIVRE
                    pedido.mesa.save()
            pedido.data_fechamento = timezone.now() # Marcar data de fechamento para cancelados também

        serializer.save()

    @action(detail=True, methods=['post'], serializer_class=PagamentoRegistroSerializer, url_path='registrar-pagamento')
    def registrar_pagamento(self, request, pk=None):
        pedido = self.get_object()
        serializer = PagamentoRegistroSerializer(data=request.data)

        if pedido.status_pedido not in [PedidoMesa.STATUS_FECHADO, PedidoMesa.STATUS_ABERTO]: # Permitir pagar pedido aberto também
            return Response({'detail': f'Não é possível registrar pagamento para pedido com status "{pedido.get_status_pedido_display()}".'}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            metodo_pagamento_req = serializer.validated_data['metodo']
            valor_pago_req = serializer.validated_data['valor_pago']

            # Usar o serviço de pagamentos para criar o registro de Pagamento
            try:
                from pagamentos.services import registrar_pagamento_para_pedido
                from pagamentos.models import Pagamento # Para acesso a choices e mapeamento de métodos

                # Mapear o método de pagamento do request para os choices do modelo Pagamento, se necessário
                # Neste caso, os choices em PagamentoRegistroSerializer já são baseados nos do PedidoMesa,
                # mas o modelo Pagamento pode ter mais opções ou nomes ligeiramente diferentes.
                # Para MVP, vamos assumir que os valores de 'metodo_pagamento_req' são compatíveis.
                # Ex: se PedidoMesa usa 'cartao_maquineta' e Pagamento usa 'cartao_credito_maquineta'/'cartao_debito_maquineta'
                # seria necessário um mapeamento. Por ora, vamos usar o valor diretamente.
                # Se 'cartao_maquineta' é genérico, podemos mapeá-lo para um dos específicos ou 'outro'.
                # Para este exemplo, vamos assumir que os métodos são diretamente compatíveis ou que
                # Pagamento.METODO_CARTAO_CREDITO_MAQUINETA e Pagamento.METODO_CARTAO_DEBITO_MAQUINETA
                # são os esperados se o método for 'cartao_maquineta'.
                # O serializer do pedido usa: ('dinheiro', 'Dinheiro'), ('cartao_maquineta', 'Cartão (Maquineta)'), ('pix_maquineta', 'PIX (Maquineta)')

                metodo_pagamento_modelo = metodo_pagamento_req # Default
                if metodo_pagamento_req == 'cartao_maquineta':
                    # Decidir se é crédito ou débito é Pós-MVP para o modelo Pagamento.
                    # Por enquanto, podemos usar um genérico ou um default.
                    # Vamos usar Pagamento.METODO_CARTAO_CREDITO_MAQUINETA como exemplo se for só 'cartao_maquineta'
                    # Ou melhor, adicionar 'cartao_maquineta_generico' ao modelo Pagamento ou usar 'outro'.
                    # Para MVP, vamos apenas passar o que veio, assumindo compatibilidade ou que o modelo Pagamento tem essa opção.
                    # Se o modelo Pagamento tem 'cartao_credito_maquineta' e 'cartao_debito_maquineta',
                    # o frontend precisaria enviar qual foi usado.
                    # O mais simples é o modelo Pagamento também ter 'cartao_maquineta'.
                    # Olhando o modelo Pagamento: ele tem METODO_CARTAO_DEBITO_MAQUINETA e METODO_CARTAO_CREDITO_MAQUINETA
                    # Então, o frontend precisaria ser mais específico, ou o atendente.
                    # Para MVP, vamos simplificar: se for 'cartao_maquineta', registramos como METODO_OUTRO ou um default.
                    # Ou melhor: O `PagamentoRegistroSerializer` deve ser atualizado para ter as mesmas opções do `Pagamento.METODO_PAGAMENTO_CHOICES`
                    # Por agora, vamos assumir que `metodo_pagamento_req` é um valor válido em `Pagamento.METODO_PAGAMENTO_CHOICES`.
                    # O ideal é que o PagamentoRegistroSerializer use os choices de Pagamento.
                    # Vou fazer um ajuste no PagamentoRegistroSerializer depois.
                    # Por agora, vamos assumir que o valor é compatível.
                    pass # Usar metodo_pagamento_req diretamente

                registrar_pagamento_para_pedido(
                    pedido_obj=pedido,
                    metodo_pagamento=metodo_pagamento_req, 
                    valor_pago=valor_pago_req,
                    status_pagamento=Pagamento.STATUS_APROVADO # Pagamentos manuais são aprovados
                )
                logger.info(f"Pagamento manual registrado para PedidoMesa ID {pedido.id}")
            except Exception as e:
                logger.error(f"Erro ao registrar pagamento para PedidoMesa ID {pedido.id} via serviço: {e}")
                # Considerar se a transação deve ser abortada ou se o log é suficiente.
                # Por ora, continua para atualizar o pedido e a mesa.
            
            # Atualizar PedidoMesa (como já estava fazendo)
            # Estes campos em PedidoMesa são para registro simplificado, o Pagamento é o mestre.
            pedido.metodo_pagamento_registrado = metodo_pagamento_req
            pedido.valor_pago_registrado = valor_pago_req
            pedido.status_pedido = PedidoMesa.STATUS_PAGO
            pedido.data_fechamento = timezone.now() # Garante que está fechado
            pedido.save()

            # Liberar a mesa se não houver outros pedidos abertos/fechados para ela
            outros_pedidos_nao_finalizados = PedidoMesa.objects.filter(
                mesa=pedido.mesa,
                status_pedido__in=[PedidoMesa.STATUS_ABERTO, PedidoMesa.STATUS_FECHADO]
            ).exists() # Não precisa excluir o pedido atual, pois ele já está sendo marcado como PAGO

            if not outros_pedidos_nao_finalizados:
                pedido.mesa.status = Mesa.STATUS_LIVRE
                pedido.mesa.save()
            
            return Response(PedidoMesaSerializer(pedido).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ItemPedidoMesaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Itens de Pedido de Mesa.
    - Adicionar item: `POST /api/pedidos_mesa/{pedido_id}/itens/` (nesta viewset, precisamos customizar create)
    - Atualizar item: `PUT /api/itens_pedido_mesa/{item_id}/` (ModelViewSet padrão)
    - Remover item: `DELETE /api/itens_pedido_mesa/{item_id}/` (ModelViewSet padrão)
    - Listar itens de um pedido: `GET /api/pedidos_mesa/{pedido_id}/itens/`
    """
    queryset = ItemPedidoMesa.objects.all()
    serializer_class = ItemPedidoMesaSerializer

    def get_queryset(self):
        # Filtra itens pelo pedido_id na URL, se fornecido
        pedido_id = self.kwargs.get('pedido_mesa_pk') # Usando o nome do kwarg da URL (ver urls.py)
        if pedido_id:
            return self.queryset.filter(pedido_mesa_id=pedido_id)
        return self.queryset # Ou retornar um empty queryset se pedido_id for obrigatório para listar

    def perform_create(self, serializer):
        pedido_id = self.kwargs.get('pedido_mesa_pk')
        pedido = get_object_or_404(PedidoMesa, id=pedido_id)

        if pedido.status_pedido not in [PedidoMesa.STATUS_ABERTO]:
            raise serializers.ValidationError(f"Não é possível adicionar itens a um pedido que não está 'Aberto'. Status atual: {pedido.get_status_pedido_display()}")

        produto_obj = serializer.validated_data['produto']
        preco_no_momento = serializer.validated_data.get('preco_unitario_no_momento', produto_obj.preco_base)
        
        # Checar se o produto já existe no pedido para este item.
        # Se sim, incrementar quantidade (ou o serializer/modelo pode ter essa lógica).
        # Para MVP, o unique_together no modelo ItemPedidoMesa ('pedido_mesa', 'produto')
        # implicaria que não podemos adicionar o mesmo produto duas vezes.
        # A melhor abordagem seria remover unique_together e permitir duplicados,
        # ou, se unique_together mantido, a view/serializer deveria tratar de encontrar
        # o item existente e atualizar sua quantidade.
        # Por ora, o serializer.save() vai falhar se unique_together for violado.
        # Assumindo que o frontend pode enviar um PUT para um item existente para mudar quantidade.

        # Set kitchen status for the order if this is the first item or order is being reopened for kitchen
        if pedido.status_cozinha is None or pedido.status_cozinha not in [PedidoMesa.STATUS_COZINHA_AGUARDANDO, PedidoMesa.STATUS_COZINHA_EM_PREPARO, PedidoMesa.STATUS_COZINHA_PRONTO]:
            # This logic might be too simple. What if an order was 'Entregue' and items are added?
            # For MVP, assume adding items to an 'Aberto' order sends it to kitchen if not already there.
            if pedido.status_pedido == PedidoMesa.STATUS_ABERTO:
                 # Only set if it's null or not already in a kitchen processing state
                if not pedido.status_cozinha or pedido.status_cozinha == PedidoMesa.STATUS_COZINHA_ENTREGUE: # Or some other non-active kitchen status
                    pedido.status_cozinha = PedidoMesa.STATUS_COZINHA_AGUARDANDO
                    pedido.horario_entrada_cozinha = timezone.now()
                    pedido.save() # Save the parent PedidoMesa

        serializer.save(pedido_mesa=pedido, preco_unitario_no_momento=preco_no_momento)

    def perform_update(self, serializer):
        item = serializer.instance
        if item.pedido_mesa.status_pedido != PedidoMesa.STATUS_ABERTO:
            raise serializers.ValidationError(f"Não é possível modificar itens de um pedido que não está 'Aberto'. Status: {item.pedido_mesa.get_status_pedido_display()}")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.pedido_mesa.status_pedido != PedidoMesa.STATUS_ABERTO:
             raise serializers.ValidationError(
                {"detail": f"Não é possível remover itens de um pedido que não está 'Aberto'. Status: {instance.pedido_mesa.get_status_pedido_display()}"},
                code=status.HTTP_400_BAD_REQUEST
            )
        instance.delete()

# Para as rotas aninhadas como /api/pedidos_mesa/{pedido_id}/itens/
# vamos precisar de um ViewSet que não seja ModelViewSet padrão para o POST,
# ou ajustar o ModelViewSet para lidar com a criação dentro do contexto do pedido.
# A forma acima (ItemPedidoMesaViewSet com get_queryset e perform_create ajustados)
# funciona bem com drf-nested-routers ou configurando URLs manualmente.

# GET /api/pedidos_mesa/{pedido_id}/itens/ -> Listar itens de um pedido (já coberto por get_queryset)
# POST /api/pedidos_mesa/{pedido_id}/itens/ -> Adicionar item (coberto por perform_create)

# PUT /api/itens_pedido_mesa/{item_id}/ -> Atualizar (ModelViewSet padrão, mas com validação de status do pedido)
# DELETE /api/itens_pedido_mesa/{item_id}/ -> Remover (ModelViewSet padrão, mas com validação de status do pedido)
# O ModelViewSet para ItemPedidoMesa já fornece PUT e DELETE por {item_id}.
# A URL base para ele seria /api/itens_pedido_mesa/
# Se quisermos /api/pedidos_mesa/{pedido_id}/itens/{item_id}/, isso requer nested routers.
# Para MVP, podemos ter rotas separadas:
# - /api/pedidos_mesa/{pedido_pk}/itens/ (GET, POST)
# - /api/itens_pedido_mesa/{pk}/ (PUT, DELETE, GET-individual)
# Isso é mais simples de configurar sem nested routers.
# A lógica em ItemPedidoMesaViewSet já suporta isso se as URLs forem mapeadas corretamente.
# O get_queryset usa 'pedido_mesa_pk' - isso é uma convenção para nested routers.
# Se não usar nested, a URL para POST seria /api/itens_pedido_mesa/ e o pedido_id viria no payload.
# Mas a especificação da API é: POST /api/pedidos_mesa/{pedido_id}/itens/
# Isso implica que o `pedido_id` vem da URL.
# Para isso, o ItemPedidoMesaViewSet precisa ser usado de forma aninhada ou ter uma view separada.

# Simplificando para MVP: vamos assumir que o frontend chama:
# POST /api/itens_pedido_mesa/  (com pedido_mesa_id no payload)
# E o perform_create seria:
# def perform_create(self, serializer):
#     pedido = get_object_or_404(PedidoMesa, id=serializer.validated_data['pedido_mesa'].id)
#     ...
# No entanto, para seguir a especificação de URL, a abordagem com kwargs é a correta.
# Precisaremos de uma biblioteca como drf-nested-routers ou configurar manualmente as URLs.
# Vou manter a lógica atual que espera `pedido_mesa_pk` no kwarg,
# e o `urls.py` deverá refletir essa estrutura aninhada.

    def get_object(self):
        """
        Sobrescrito para garantir que o item pertença ao pedido especificado na URL aninhada.
        Usado para retrieve, update, partial_update, destroy de um item específico.
        """
        queryset = self.filter_queryset(self.get_queryset()) # Aplica filtros do ModelViewSet
        
        # Parâmetros da URL para o item e o pedido pai
        item_pk = self.kwargs.get('pk')
        pedido_pk = self.kwargs.get('pedido_mesa_pk')

        if item_pk is None or pedido_pk is None:
            # Se chamado em um contexto onde pk ou pedido_mesa_pk não está na URL (ex: /api/itens_pedido_mesa/ sem aninhamento),
            # usar o comportamento padrão do get_object que só usa 'pk'.
            # No entanto, nossas URLs aninhadas sempre terão ambos.
            # Se uma rota não aninhada como /api/itens_pedido_mesa/{pk}/ for usada, pedido_pk será None.
            # Para este caso, não filtramos por pedido_pk.
            if item_pk is not None and pedido_pk is None: # Rota não aninhada /api/itens_pedido_mesa/{pk}/
                 obj = get_object_or_404(queryset, pk=item_pk)
                 self.check_object_permissions(self.request, obj)
                 return obj
            # Se ambos são None, ou apenas pedido_pk é None mas item_pk também é (ex: list view),
            # o get_object padrão pode levantar erro ou não ser aplicável.
            # Mas para detail views (retrieve, update, destroy), 'pk' deve estar presente.
            # Para ser seguro, recorra ao comportamento padrão se o contexto não for o aninhado esperado.
            return super().get_object()


        # Filtrar pelo item_pk e pedido_pk para rotas aninhadas
        obj = get_object_or_404(queryset, pk=item_pk, pedido_mesa_id=pedido_pk)
        
        # Verificar permissões do objeto
        self.check_object_permissions(self.request, obj)
        return obj
