from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status

from whatsapp_bot.models import PedidoWhatsApp
from atendimento_interno.models import PedidoMesa, Mesa, ItemPedidoMesa
# from products.models import ProdutoPlaceholder as Produto # Using placeholder from administracao for now
from administracao.models import ProdutoPlaceholder, CategoriaProdutoPlaceholder

# Refer to TESTING_STRATEGY.md for overall testing guidelines.

class CozinhaAPITests(APITestCase):
    def setUp(self):
        # Categoria e Produto (usando placeholders da app de administração)
        self.categoria_cozinha = CategoriaProdutoPlaceholder.objects.create(nome="Cozinha Test Categoria")
        self.produto_cozinha = ProdutoPlaceholder.objects.create(
            nome="Produto Cozinha Teste",
            preco_base=10.00,
            categoria=self.categoria_cozinha
        )

        # Pedido WhatsApp para teste
        self.pedido_whatsapp = PedidoWhatsApp.objects.create(
            telefone_cliente="+5511911112222",
            estado_conversa='FINALIZADO', # Supõe que passou pelo fluxo do bot
            carrinho_atual=[
                {'id': self.produto_cozinha.id, 'nome': self.produto_cozinha.nome, 'preco': float(self.produto_cozinha.preco_base), 'quantidade': 2, 'observacoes': 'Sem cebola WP'}
            ],
            status_cozinha=PedidoWhatsApp.STATUS_COZINHA_AGUARDANDO,
            horario_entrada_cozinha=timezone.now() - timezone.timedelta(minutes=10) # Entrou há 10 mins
        )

        # Pedido de Mesa para teste
        self.mesa_cozinha = Mesa.objects.create(numero_identificador="C01")
        self.pedido_mesa = PedidoMesa.objects.create(
            mesa=self.mesa_cozinha,
            status_pedido=PedidoMesa.STATUS_ABERTO, # Ou Fechado, dependendo de quando vai pra cozinha
            status_cozinha=PedidoMesa.STATUS_COZINHA_AGUARDANDO,
            horario_entrada_cozinha=timezone.now() - timezone.timedelta(minutes=5) # Entrou há 5 mins
        )
        ItemPedidoMesa.objects.create(
            pedido_mesa=self.pedido_mesa,
            produto=self.produto_cozinha,
            quantidade=1,
            preco_unitario_no_momento=self.produto_cozinha.preco_base,
            observacoes_item="Bem passado PM"
        )
        
        # Pedido de Mesa que está em preparo
        self.mesa_cozinha_2 = Mesa.objects.create(numero_identificador="C02")
        self.pedido_mesa_em_preparo = PedidoMesa.objects.create(
            mesa=self.mesa_cozinha_2,
            status_pedido=PedidoMesa.STATUS_ABERTO,
            status_cozinha=PedidoMesa.STATUS_COZINHA_EM_PREPARO,
            horario_entrada_cozinha=timezone.now() - timezone.timedelta(minutes=2)
        )
        ItemPedidoMesa.objects.create(
            pedido_mesa=self.pedido_mesa_em_preparo,
            produto=self.produto_cozinha,
            quantidade=3,
            preco_unitario_no_momento=self.produto_cozinha.preco_base
        )


    def test_listar_pedidos_para_preparar(self):
        """ Testa GET /api/cozinha/pedidos_para_preparar/ """
        url = reverse('cozinha_api:pedidos_para_preparar_list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3) # Espera os 3 pedidos criados no setUp

        # Verificar a ordenação (pedido_whatsapp deve vir primeiro por ser mais antigo)
        # O horario_entrada_cozinha foi setado para isso
        ids_origem_ordenados = [p['id_pedido_origem'] for p in response.data]
        tipos_origem_ordenados = [p['tipo_origem'] for p in response.data]
        
        # self.pedido_whatsapp (10 min atrás), self.pedido_mesa (5 min atrás), self.pedido_mesa_em_preparo (2 min atrás)
        expected_ids_order = [self.pedido_whatsapp.id, self.pedido_mesa.id, self.pedido_mesa_em_preparo.id]
        expected_tipos_order = ['WhatsApp', 'Mesa', 'Mesa']

        self.assertEqual(ids_origem_ordenados, expected_ids_order)
        self.assertEqual(tipos_origem_ordenados, expected_tipos_order)

        # Verificar estrutura de um dos pedidos (ex: o primeiro, que é o WhatsApp)
        pedido_wp_data = response.data[0]
        self.assertEqual(pedido_wp_data['id_pedido_origem'], self.pedido_whatsapp.id)
        self.assertEqual(pedido_wp_data['tipo_origem'], 'WhatsApp')
        self.assertEqual(pedido_wp_data['status_cozinha_atual'], PedidoWhatsApp.STATUS_COZINHA_AGUARDANDO)
        self.assertEqual(len(pedido_wp_data['itens']), 1)
        self.assertEqual(pedido_wp_data['itens'][0]['nome_produto'], self.produto_cozinha.nome)
        self.assertEqual(pedido_wp_data['itens'][0]['quantidade'], 2)
        self.assertEqual(pedido_wp_data['itens'][0]['observacoes_item'], 'Sem cebola WP')

        # Verificar estrutura de um pedido de mesa
        pedido_mesa_data = response.data[1] # O segundo na ordem
        self.assertEqual(pedido_mesa_data['id_pedido_origem'], self.pedido_mesa.id)
        self.assertEqual(pedido_mesa_data['tipo_origem'], 'Mesa')
        self.assertEqual(pedido_mesa_data['status_cozinha_atual'], PedidoMesa.STATUS_COZINHA_AGUARDANDO)
        self.assertEqual(len(pedido_mesa_data['itens']), 1)
        self.assertEqual(pedido_mesa_data['itens'][0]['nome_produto'], self.produto_cozinha.nome)
        self.assertEqual(pedido_mesa_data['itens'][0]['quantidade'], 1)
        self.assertEqual(pedido_mesa_data['itens'][0]['observacoes_item'], 'Bem passado PM')


    def test_atualizar_status_cozinha_pedido_whatsapp(self):
        """ Testa PATCH /api/cozinha/pedidos/whatsapp/{id_pedido}/status/ """
        url = reverse('cozinha_api:atualizar_status_cozinha', kwargs={
            'tipo_origem': 'whatsapp',
            'id_pedido_origem': self.pedido_whatsapp.id
        })
        
        # 1. Mudar de AguardandoPreparo para EmPreparo
        data_em_preparo = {'status_cozinha': PedidoWhatsApp.STATUS_COZINHA_EM_PREPARO}
        response = self.client.patch(url, data_em_preparo, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pedido_whatsapp.refresh_from_db()
        self.assertEqual(self.pedido_whatsapp.status_cozinha, PedidoWhatsApp.STATUS_COZINHA_EM_PREPARO)
        self.assertEqual(response.data['status_cozinha_novo'], PedidoWhatsApp.STATUS_COZINHA_EM_PREPARO)

        # 2. Mudar de EmPreparo para Pronto
        data_pronto = {'status_cozinha': PedidoWhatsApp.STATUS_COZINHA_PRONTO}
        response = self.client.patch(url, data_pronto, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pedido_whatsapp.refresh_from_db()
        self.assertEqual(self.pedido_whatsapp.status_cozinha, PedidoWhatsApp.STATUS_COZINHA_PRONTO)
        self.assertEqual(response.data['status_cozinha_novo'], PedidoWhatsApp.STATUS_COZINHA_PRONTO)

    def test_atualizar_status_cozinha_pedido_mesa(self):
        """ Testa PATCH /api/cozinha/pedidos/mesa/{id_pedido}/status/ """
        url = reverse('cozinha_api:atualizar_status_cozinha', kwargs={
            'tipo_origem': 'mesa',
            'id_pedido_origem': self.pedido_mesa.id # Este está AguardandoPreparo
        })
        
        data_em_preparo = {'status_cozinha': PedidoMesa.STATUS_COZINHA_EM_PREPARO}
        response = self.client.patch(url, data_em_preparo, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pedido_mesa.refresh_from_db()
        self.assertEqual(self.pedido_mesa.status_cozinha, PedidoMesa.STATUS_COZINHA_EM_PREPARO)

    def test_atualizar_status_cozinha_transicao_invalida(self):
        """ Testa transição de status inválida (ex: AguardandoPreparo para Pronto) """
        # self.pedido_whatsapp está AguardandoPreparo
        url = reverse('cozinha_api:atualizar_status_cozinha', kwargs={
            'tipo_origem': 'whatsapp',
            'id_pedido_origem': self.pedido_whatsapp.id
        })
        data_pronto_direto = {'status_cozinha': PedidoWhatsApp.STATUS_COZINHA_PRONTO}
        response = self.client.patch(url, data_pronto_direto, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Status inválido', response.data.get('detail', '')) # Checa a mensagem de erro da view

    def test_atualizar_status_cozinha_status_nao_permitido_pela_api(self):
        """ Testa tentar mudar para um status não permitido pela API (ex: Entregue) """
        url = reverse('cozinha_api:atualizar_status_cozinha', kwargs={
            'tipo_origem': 'whatsapp',
            'id_pedido_origem': self.pedido_whatsapp.id
        })
        # O serializer KitchenStatusUpdateSerializer só permite EmPreparo ou Pronto
        data_entregue = {'status_cozinha': PedidoWhatsApp.STATUS_COZINHA_ENTREGUE}
        response = self.client.patch(url, data_entregue, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) # Erro do serializer
        self.assertIn('status_cozinha', response.data) # O serializer deve retornar erro no campo

    def test_atualizar_status_pedido_nao_encontrado(self):
        """ Testa PATCH com ID de pedido inexistente """
        url = reverse('cozinha_api:atualizar_status_cozinha', kwargs={
            'tipo_origem': 'mesa',
            'id_pedido_origem': 99999 # ID inexistente
        })
        data = {'status_cozinha': PedidoMesa.STATUS_COZINHA_EM_PREPARO}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Outros cenários para testar:
    # - Pedido já 'Pronto' não pode ser alterado por esta API.
    # - Tipo de origem inválido (ex: 'email').
    # - ID de pedido com formato inválido.
```
