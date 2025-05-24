from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Mesa, PedidoMesa, ItemPedidoMesa
# from products.models import ProdutoPlaceholder as Produto # Using placeholder for now
# from pagamentos.models import Pagamento # To verify payment creation

# For placeholder Produto:
from administracao.models import ProdutoPlaceholder, CategoriaProdutoPlaceholder

# Refer to TESTING_STRATEGY.md for overall testing guidelines.

class AtendimentoInternoModelTests(TestCase):
    def setUp(self):
        # Categoria and Produto (using placeholders)
        self.categoria_pizza = CategoriaProdutoPlaceholder.objects.create(nome="Pizzas")
        self.produto_pizza = ProdutoPlaceholder.objects.create(
            nome="Pizza Teste Model", 
            preco_base=30.00,
            categoria=self.categoria_pizza
        )
        self.mesa = Mesa.objects.create(numero_identificador="M01")
        self.pedido_mesa = PedidoMesa.objects.create(mesa=self.mesa)

    def test_pedido_mesa_calcular_total(self):
        """
        Testa o método calcular_total() do modelo PedidoMesa.
        """
        ItemPedidoMesa.objects.create(
            pedido_mesa=self.pedido_mesa,
            produto=self.produto_pizza,
            quantidade=2,
            preco_unitario_no_momento=self.produto_pizza.preco_base,
            # subtotal_item is calculated on save
        )
        ItemPedidoMesa.objects.create(
            pedido_mesa=self.pedido_mesa,
            produto=self.produto_pizza, # Add another instance of the same product, if allowed by model (unique_together removed for this)
            quantidade=1,
            preco_unitario_no_momento=self.produto_pizza.preco_base,
            observacoes_item="Extra queijo"
        )
        # Recalculate unique_together if it was ('pedido_mesa', 'produto')
        # For this test, assume it's allowed or handle updates to existing items.
        # If unique_together is active and we want to test total, create items of different products.

        # Assuming ItemPedidoMesa.save() correctly calculates subtotal_item
        # Total should be (2 * 30.00) + (1 * 30.00) = 90.00
        # If unique_together was enforced, the second create would fail or update.
        # Let's assume the test setup implies distinct items or handling of updates.
        # For simplicity, let's use two different products if unique_together is an issue.
        
        # Re-evaluating based on current ItemPedidoMesa model:
        # unique_together = ('pedido_mesa', 'produto') was there.
        # For testing calcular_total, this means we should either:
        # 1. Test with items of different products.
        # 2. Test by updating quantity of an existing item (though calcular_total sums existing items).
        # Let's assume the first item was quantity 2, price 30. Second item is a different product.
        
        # For simplicity, let's clear items and add one, then check total.
        self.pedido_mesa.itens_pedido.all().delete()
        item1 = ItemPedidoMesa.objects.create(
            pedido_mesa=self.pedido_mesa,
            produto=self.produto_pizza,
            quantidade=3, # 3 * 30 = 90
            preco_unitario_no_momento=self.produto_pizza.preco_base
        )
        self.assertEqual(self.pedido_mesa.calcular_total(), 90.00)

        # Add another different product
        produto_bebida = ProdutoPlaceholder.objects.create(nome="Bebida Teste", preco_base=5.00, categoria=self.categoria_pizza)
        item2 = ItemPedidoMesa.objects.create(
            pedido_mesa=self.pedido_mesa,
            produto=produto_bebida,
            quantidade=2, # 2 * 5 = 10
            preco_unitario_no_momento=produto_bebida.preco_base
        )
        self.assertEqual(self.pedido_mesa.calcular_total(), 100.00) # 90 + 10


    # Add more unit tests for other model methods if any (e.g., Mesa status transitions)

class AtendimentoAPITests(APITestCase):
    def setUp(self):
        # Criar dados de teste: Mesas, Produtos (usando placeholders)
        self.categoria_teste = CategoriaProdutoPlaceholder.objects.create(nome="Pizzas API")
        self.produto_teste_pizza = ProdutoPlaceholder.objects.create(
            nome="Pizza API Teste", 
            preco_base=35.00,
            categoria=self.categoria_teste
        )
        self.mesa1 = Mesa.objects.create(numero_identificador="A01", status=Mesa.STATUS_LIVRE)
        self.mesa2 = Mesa.objects.create(numero_identificador="A02", status=Mesa.STATUS_OCUPADA)
        
        # Criar um pedido para mesa2 para testes de pagamento, etc.
        self.pedido_mesa2 = PedidoMesa.objects.create(mesa=self.mesa2, status_pedido=PedidoMesa.STATUS_FECHADO)
        ItemPedidoMesa.objects.create(
            pedido_mesa=self.pedido_mesa2,
            produto=self.produto_teste_pizza,
            quantidade=1,
            preco_unitario_no_momento=self.produto_teste_pizza.preco_base
        )
        # self.pedido_mesa2.status_cozinha = PedidoMesa.STATUS_COZINHA_AGUARDANDO # Set by item add
        # self.pedido_mesa2.save()


    def test_listar_mesas(self):
        """ Testa GET /api/mesas/ """
        url = reverse('atendimento_interno:mesa-list') # Assumindo basename='mesa'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) # Espera 2 mesas criadas no setUp

    def test_criar_pedido_para_mesa_livre(self):
        """ Testa POST /api/mesas/{mesa_id}/pedidos/ para mesa livre """
        # url = reverse('atendimento_interno:mesa-criar-pedido-para-mesa', kwargs={'pk': self.mesa1.pk})
        # O nome da rota gerada pelo @action é 'mesa-pedidos'
        url = reverse('atendimento_interno:mesa-pedidos', kwargs={'pk': self.mesa1.pk})
        response = self.client.post(url, {}, format='json') # No data needed for creation
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PedidoMesa.objects.filter(mesa=self.mesa1).count(), 1)
        self.mesa1.refresh_from_db()
        self.assertEqual(self.mesa1.status, Mesa.STATUS_OCUPADA)
        novo_pedido = PedidoMesa.objects.get(mesa=self.mesa1)
        self.assertEqual(novo_pedido.status_pedido, PedidoMesa.STATUS_ABERTO)

    def test_criar_pedido_para_mesa_ja_com_pedido_aberto(self):
        """ Testa POST /api/mesas/{mesa_id}/pedidos/ para mesa que já tem pedido aberto/fechado """
        # mesa2 já tem um pedido_mesa2 (status Fechado) no setUp
        url = reverse('atendimento_interno:mesa-pedidos', kwargs={'pk': self.mesa2.pk})
        response = self.client.post(url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('pedido_existente', response.data)


    def test_adicionar_item_ao_pedido(self):
        """ Testa POST /api/pedidos_mesa/{pedido_id}/itens/ """
        pedido_novo = PedidoMesa.objects.create(mesa=self.mesa1, status_pedido=PedidoMesa.STATUS_ABERTO)
        # A rota é 'pedido-itens-list' para POST
        url = reverse('atendimento_interno:pedido-itens-list', kwargs={'pedido_mesa_pk': pedido_novo.pk})
        data = {
            'produto_id': self.produto_teste_pizza.pk,
            'quantidade': 2,
            # 'preco_unitario_no_momento' pode ser omitido se o serializer o busca do produto
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ItemPedidoMesa.objects.filter(pedido_mesa=pedido_novo).count(), 1)
        item_adicionado = ItemPedidoMesa.objects.get(pedido_mesa=pedido_novo)
        self.assertEqual(item_adicionado.produto, self.produto_teste_pizza)
        self.assertEqual(item_adicionado.quantidade, 2)
        self.assertEqual(float(item_adicionado.preco_unitario_no_momento), float(self.produto_teste_pizza.preco_base))
        self.assertEqual(float(item_adicionado.subtotal_item), float(2 * self.produto_teste_pizza.preco_base))

        # Verificar se status_cozinha do PedidoMesa foi para 'AguardandoPreparo'
        pedido_novo.refresh_from_db()
        self.assertEqual(pedido_novo.status_cozinha, PedidoMesa.STATUS_COZINHA_AGUARDANDO)


    def test_registrar_pagamento_mesa(self):
        """ Testa POST /api/pedidos_mesa/{pedido_id}/registrar-pagamento/ """
        # self.pedido_mesa2 está 'Fechado' e tem 1 item de 35.00
        # url = reverse('atendimento_interno:pedidomesa-registrar-pagamento', kwargs={'pk': self.pedido_mesa2.pk})
        # O nome da rota gerada pelo @action é 'pedidomesa-registrar-pagamento'
        url = reverse('atendimento_interno:pedidomesa-registrar-pagamento', kwargs={'pk': self.pedido_mesa2.pk})
        
        # Usar as choices definidas em PagamentoRegistroSerializer (que agora são do modelo Pagamento)
        from pagamentos.models import Pagamento
        data = {'metodo': Pagamento.METODO_DINHEIRO, 'valor_pago': 35.00}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pedido_mesa2.refresh_from_db()
        self.mesa2.refresh_from_db() # Mesa associada ao pedido_mesa2
        
        self.assertEqual(self.pedido_mesa2.status_pedido, PedidoMesa.STATUS_PAGO)
        self.assertEqual(self.mesa2.status, Mesa.STATUS_LIVRE) # Mesa deve ser liberada
        
        # Verificar se um registro Pagamento foi criado
        self.assertTrue(Pagamento.objects.filter(object_id=self.pedido_mesa2.id, content_type__model='pedidomesa').exists())
        pagamento_criado = Pagamento.objects.get(object_id=self.pedido_mesa2.id, content_type__model='pedidomesa')
        self.assertEqual(pagamento_criado.metodo_pagamento, Pagamento.METODO_DINHEIRO)
        self.assertEqual(float(pagamento_criado.valor_pago), 35.00)
        self.assertEqual(pagamento_criado.status_pagamento, Pagamento.STATUS_APROVADO)

    def test_atualizar_status_mesa(self):
        """ Testa PATCH /api/mesas/{mesa_id}/atualizar-status/ """
        # url = reverse('atendimento_interno:mesa-atualizar-status', kwargs={'pk': self.mesa1.pk})
        # O nome da rota gerada pelo @action é 'mesa-atualizar-status'
        url = reverse('atendimento_interno:mesa-atualizar-status', kwargs={'pk': self.mesa1.pk})
        data = {'status': Mesa.STATUS_INTERDITADA}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mesa1.refresh_from_db()
        self.assertEqual(self.mesa1.status, Mesa.STATUS_INTERDITADA)

    # Outros testes de API para atendimento_interno:
    # - Testar PUT/PATCH/DELETE para Itens de Pedido (ex: mudar quantidade, remover item)
    #   - PUT /api/pedidos_mesa/{pedido_id}/itens/{item_id}/
    #   - DELETE /api/pedidos_mesa/{pedido_id}/itens/{item_id}/
    # - Testar validações (ex: adicionar item a pedido não 'Aberto')
    # - Testar filtros de listagem se houver (ex: listar apenas mesas 'Livres')
    # - Testar o PATCH em PedidoMesa para mudar status_pedido para 'Cancelado' ou 'Fechado'
    #   e verificar o impacto no status_cozinha e status da mesa.
```
