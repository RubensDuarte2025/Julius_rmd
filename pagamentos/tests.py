from django.test import TestCase
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch # For mocking parts of services if needed

from .models import Pagamento
from .services import registrar_pagamento_para_pedido
from whatsapp_bot.models import PedidoWhatsApp
from atendimento_interno.models import PedidoMesa, Mesa
# from products.models import ProdutoPlaceholder # If needed for creating PedidoMesa items
from administracao.models import ProdutoPlaceholder, CategoriaProdutoPlaceholder


# Refer to TESTING_STRATEGY.md for overall testing guidelines.

class PagamentoServiceTests(TestCase):
    def setUp(self):
        # PedidoWhatsApp para teste
        self.pedido_whatsapp = PedidoWhatsApp.objects.create(
            telefone_cliente="+5511933334444",
            estado_conversa='AGUARDANDO_CONFIRMACAO_PAGAMENTO_PIX', # Estado relevante
            carrinho_atual=[{'id': 1, 'nome': 'Pizza Teste WP', 'preco': 50.00, 'quantidade': 1}]
        )

        # PedidoMesa para teste
        self.mesa_pag_svc = Mesa.objects.create(numero_identificador="P01")
        self.pedido_mesa = PedidoMesa.objects.create(
            mesa=self.mesa_pag_svc,
            status_pedido=PedidoMesa.STATUS_FECHADO # Estado relevante
        )
        # Adicionar um item para que o pedido_mesa tenha valor
        cat = CategoriaProdutoPlaceholder.objects.create(nome="Cat Pag Svc")
        prod = ProdutoPlaceholder.objects.create(nome="Prod Pag Svc", preco_base=25.00, categoria=cat)
        ItemPedidoMesa.objects.create(
            pedido_mesa=self.pedido_mesa,
            produto=prod,
            quantidade=2, # Total 50.00
            preco_unitario_no_momento=prod.preco_base
        )


    def test_registrar_pagamento_para_pedido_whatsapp(self):
        """ Testa registrar pagamento para PedidoWhatsApp """
        pagamento = registrar_pagamento_para_pedido(
            pedido_obj=self.pedido_whatsapp,
            metodo_pagamento=Pagamento.METODO_PIX,
            valor_pago=50.00, # Valor do carrinho
            status_pagamento=Pagamento.STATUS_APROVADO
        )
        self.assertIsNotNone(pagamento)
        self.assertEqual(pagamento.valor_pago, 50.00)
        self.assertEqual(pagamento.metodo_pagamento, Pagamento.METODO_PIX)
        self.assertEqual(pagamento.status_pagamento, Pagamento.STATUS_APROVADO)
        self.assertEqual(pagamento.content_type, ContentType.objects.get_for_model(PedidoWhatsApp))
        self.assertEqual(pagamento.object_id, self.pedido_whatsapp.id)
        self.assertEqual(Pagamento.objects.count(), 1)

    def test_registrar_pagamento_para_pedido_mesa(self):
        """ Testa registrar pagamento para PedidoMesa """
        pagamento = registrar_pagamento_para_pedido(
            pedido_obj=self.pedido_mesa,
            metodo_pagamento=Pagamento.METODO_DINHEIRO,
            valor_pago=50.00, # Valor do pedido_mesa
            status_pagamento=Pagamento.STATUS_APROVADO
        )
        self.assertIsNotNone(pagamento)
        self.assertEqual(pagamento.valor_pago, 50.00)
        self.assertEqual(pagamento.metodo_pagamento, Pagamento.METODO_DINHEIRO)
        self.assertEqual(pagamento.content_type, ContentType.objects.get_for_model(PedidoMesa))
        self.assertEqual(pagamento.object_id, self.pedido_mesa.id)
        self.assertEqual(Pagamento.objects.count(), 1)
    
    def test_registrar_pagamento_com_status_pendente(self):
        """ Testa registrar pagamento com status Pendente """
        pagamento = registrar_pagamento_para_pedido(
            pedido_obj=self.pedido_whatsapp,
            metodo_pagamento=Pagamento.METODO_PIX,
            valor_pago=50.00,
            status_pagamento=Pagamento.STATUS_PENDENTE # Status diferente do default
        )
        self.assertEqual(pagamento.status_pagamento, Pagamento.STATUS_PENDENTE)

    def test_registrar_pagamento_com_dados_opcionais(self):
        """ Testa registrar pagamento com transacao_id e qr_code """
        pagamento = registrar_pagamento_para_pedido(
            pedido_obj=self.pedido_mesa,
            metodo_pagamento=Pagamento.METODO_PIX,
            valor_pago=50.00,
            transacao_id_gateway="gateway_trans_id_123",
            qr_code_pix="pix_copia_cola_chave"
        )
        self.assertEqual(pagamento.transacao_id_gateway, "gateway_trans_id_123")
        self.assertEqual(pagamento.qr_code_pix_copia_cola, "pix_copia_cola_chave")

    # (Pós-MVP ou se a lógica for movida para o service)
    # @patch('pagamentos.services.PedidoWhatsApp.save') # Exemplo de mock
    # def test_registrar_pagamento_atualiza_status_pedido_whatsapp(self, mock_pedido_save):
    #     # Este teste dependeria da lógica de atualização do pedido pai ser movida para o service.
    #     # Por enquanto, essa lógica está nas views dos apps de pedido.
    #     pass


class PagamentosAPITests(APITestCase):
    def setUp(self):
        # Pedido WhatsApp
        self.pedido_wp = PedidoWhatsApp.objects.create(telefone_cliente="+5511955556666")
        Pagamento.objects.create(
            pedido=self.pedido_wp, 
            metodo_pagamento=Pagamento.METODO_PIX, 
            valor_pago=100.00,
            status_pagamento=Pagamento.STATUS_APROVADO
        )
        Pagamento.objects.create(
            pedido=self.pedido_wp, 
            metodo_pagamento=Pagamento.METODO_PIX, 
            valor_pago=10.00, # Segundo pagamento para o mesmo pedido (ex: adicional)
            status_pagamento=Pagamento.STATUS_PENDENTE
        )

        # Pedido Mesa
        self.mesa_pag_api = Mesa.objects.create(numero_identificador="P02")
        self.pedido_m = PedidoMesa.objects.create(mesa=self.mesa_pag_api)
        Pagamento.objects.create(
            pedido=self.pedido_m, 
            metodo_pagamento=Pagamento.METODO_DINHEIRO, 
            valor_pago=75.00,
            status_pagamento=Pagamento.STATUS_APROVADO
        )
        
        # Pedido sem pagamentos
        self.mesa_sem_pag = Mesa.objects.create(numero_identificador="P03")
        self.pedido_sem_pag = PedidoMesa.objects.create(mesa=self.mesa_sem_pag)


    def test_listar_pagamentos_por_pedido_whatsapp(self):
        """ Testa GET /api/pagamentos/pedido/whatsapp/{id_pedido_wp}/ """
        url = reverse('pagamentos:listar_pagamentos_por_pedido', kwargs={
            'tipo_origem': 'whatsapp', 
            'id_pedido_origem': self.pedido_wp.id
        })
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) # Dois pagamentos para self.pedido_wp
        # Verificar se os dados estão corretos, ex: o mais recente primeiro
        self.assertEqual(response.data[0]['status_pagamento'], Pagamento.STATUS_PENDENTE) # O segundo criado
        self.assertEqual(response.data[1]['status_pagamento'], Pagamento.STATUS_APROVADO) # O primeiro criado

    def test_listar_pagamentos_por_pedido_mesa(self):
        """ Testa GET /api/pagamentos/pedido/mesa/{id_pedido_m}/ """
        url = reverse('pagamentos:listar_pagamentos_por_pedido', kwargs={
            'tipo_origem': 'mesa', 
            'id_pedido_origem': self.pedido_m.id
        })
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['valor_pago'], '75.00')

    def test_listar_pagamentos_pedido_sem_pagamentos(self):
        """ Testa GET para um pedido que não tem pagamentos associados. """
        url = reverse('pagamentos:listar_pagamentos_por_pedido', kwargs={
            'tipo_origem': 'mesa', 
            'id_pedido_origem': self.pedido_sem_pag.id
        })
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0) # Espera lista vazia

    def test_listar_pagamentos_tipo_origem_invalido(self):
        """ Testa GET com tipo_origem inválido. """
        url = reverse('pagamentos:listar_pagamentos_por_pedido', kwargs={
            'tipo_origem': 'invalido', 
            'id_pedido_origem': self.pedido_wp.id
        })
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Tipo de origem', response.data.get('detail', ''))

    def test_listar_pagamentos_id_pedido_nao_encontrado(self):
        """ Testa GET com ID de pedido que não existe. """
        url = reverse('pagamentos:listar_pagamentos_por_pedido', kwargs={
            'tipo_origem': 'mesa', 
            'id_pedido_origem': 99999 # ID inexistente
        })
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) # A view foi ajustada para retornar 404
        self.assertIn('não encontrado', response.data.get('detail', ''))

    # Testes de segurança (Pós-MVP ou se permissões forem adicionadas a esta API):
    # - Acessar sem autenticação (se a API for protegida).
    # - Acessar com usuário sem permissão (se houver lógica de permissão).
```
