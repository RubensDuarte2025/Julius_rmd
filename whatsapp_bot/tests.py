from django.test import TestCase
from unittest.mock import patch, MagicMock

from .models import PedidoWhatsApp
# from .views import send_whatsapp_message # Se for testar a view diretamente

# Refer to TESTING_STRATEGY.md for overall testing guidelines.

class PedidoWhatsAppModelTests(TestCase):
    def setUp(self):
        self.pedido_conversa = PedidoWhatsApp.objects.create(telefone_cliente="+5511999998888")
        # Mock product data similar to what's used in views.py
        self.mock_produto_pizza = {'id': 101, 'nome': 'Pizza Calabresa', 'preco': 30.00}
        self.mock_produto_bebida = {'id': 301, 'nome': 'Refrigerante Lata', 'preco': 5.00}


    def test_adicionar_item_carrinho_novo_item(self):
        """ Test adding a new item to an empty cart. """
        mock_produto_obj = type('MockProduto', (), self.mock_produto_pizza)()
        self.pedido_conversa.adicionar_item_carrinho(mock_produto_obj, quantidade=1)
        self.assertEqual(len(self.pedido_conversa.carrinho_atual), 1)
        self.assertEqual(self.pedido_conversa.carrinho_atual[0]['nome'], 'Pizza Calabresa')
        self.assertEqual(self.pedido_conversa.carrinho_atual[0]['quantidade'], 1)

    def test_adicionar_item_carrinho_atualizar_quantidade(self):
        """ Test adding an existing item to update its quantity. """
        mock_produto_obj_pizza = type('MockProduto', (), self.mock_produto_pizza)()
        self.pedido_conversa.adicionar_item_carrinho(mock_produto_obj_pizza, quantidade=1)
        self.pedido_conversa.adicionar_item_carrinho(mock_produto_obj_pizza, quantidade=2)
        
        self.assertEqual(len(self.pedido_conversa.carrinho_atual), 1)
        self.assertEqual(self.pedido_conversa.carrinho_atual[0]['quantidade'], 3)

    def test_remover_ultimo_item_carrinho(self):
        """ Test removing the last item from the cart. """
        mock_produto_obj_pizza = type('MockProduto', (), self.mock_produto_pizza)()
        mock_produto_obj_bebida = type('MockProduto', (), self.mock_produto_bebida)()
        self.pedido_conversa.adicionar_item_carrinho(mock_produto_obj_pizza)
        self.pedido_conversa.adicionar_item_carrinho(mock_produto_obj_bebida)
        
        self.assertTrue(self.pedido_conversa.remover_ultimo_item_carrinho())
        self.assertEqual(len(self.pedido_conversa.carrinho_atual), 1)
        self.assertEqual(self.pedido_conversa.carrinho_atual[0]['nome'], 'Pizza Calabresa')

    def test_remover_ultimo_item_carrinho_vazio(self):
        """ Test removing from an empty cart. """
        self.assertFalse(self.pedido_conversa.remover_ultimo_item_carrinho())
        self.assertEqual(len(self.pedido_conversa.carrinho_atual), 0)

    def test_calcular_total_carrinho(self):
        """ Test calculating the total price of the cart. """
        mock_produto_obj_pizza = type('MockProduto', (), self.mock_produto_pizza)()
        mock_produto_obj_bebida = type('MockProduto', (), self.mock_produto_bebida)()
        self.pedido_conversa.adicionar_item_carrinho(mock_produto_obj_pizza, quantidade=2) # 2 * 30.00 = 60.00
        self.pedido_conversa.adicionar_item_carrinho(mock_produto_obj_bebida, quantidade=1) # 1 * 5.00 = 5.00
        
        self.assertEqual(self.pedido_conversa.calcular_total_carrinho(), 65.00)

    def test_reset_conversa(self):
        """ Test resetting the conversation state. """
        mock_produto_obj_pizza = type('MockProduto', (), self.mock_produto_pizza)()
        self.pedido_conversa.adicionar_item_carrinho(mock_produto_obj_pizza)
        self.pedido_conversa.estado_conversa = 'AGUARDANDO_ESCOLHA_PRODUTO'
        self.pedido_conversa.dados_temporarios = {'categoria_selecionada': '1'}
        self.pedido_conversa.save()

        self.pedido_conversa.reset_conversa()
        self.assertEqual(self.pedido_conversa.estado_conversa, 'INICIO')
        self.assertEqual(len(self.pedido_conversa.carrinho_atual), 0)
        self.assertEqual(self.pedido_conversa.dados_temporarios, {})


class WhatsAppWebhookViewTests(TestCase):
    # These tests would typically use Django's test client or APIRequestFactory
    # to simulate POST requests to the webhook view.
    # For simplicity and focus on state machine logic, we might call a helper function
    # that encapsulates the core logic of the view if it's refactored,
    # or patch external dependencies like `send_whatsapp_message`.

    def setUp(self):
        # Initial data setup for each test method if needed
        pass

    @patch('whatsapp_bot.views.send_whatsapp_message') # Mock the function that sends messages
    def test_webhook_inicio_conversa_opcao_1_cardapio(self, mock_send_message):
        """
        Testa o fluxo inicial: nova conversa -> envia '1' (Ver Cardápio).
        Verifica a mudança de estado e a mensagem de resposta.
        """
        # Simulate POST request data
        # client = Client()
        # response = client.post(reverse('whatsapp_bot:whatsapp_webhook'), {
        #     'From': 'whatsapp:+5511999997777',
        #     'Body': 'Olá' # Simula primeira mensagem
        # })
        # self.assertEqual(response.status_code, 200)
        # pedido_conversa = PedidoWhatsApp.objects.get(telefone_cliente='+5511999997777')
        # self.assertEqual(pedido_conversa.estado_conversa, 'AGUARDANDO_OPCAO_INICIAL')
        # mock_send_message.assert_called_with(
        #     '+5511999997777',
        #     "Olá! Bem-vindo à Pizzaria [Nome da Pizzaria]! 😊\nDigite:\n1️⃣ Ver Cardápio e Fazer Pedido 🍕\n2️⃣ Falar com um Atendente 💬"
        # )
        
        # response_opcao1 = client.post(reverse('whatsapp_bot:whatsapp_webhook'), {
        #     'From': 'whatsapp:+5511999997777',
        #     'Body': '1'
        # })
        # self.assertEqual(response_opcao1.status_code, 200)
        # pedido_conversa.refresh_from_db()
        # self.assertEqual(pedido_conversa.estado_conversa, 'AGUARDANDO_ESCOLHA_CATEGORIA')
        # # Check that send_whatsapp_message was called with the category list
        # # Example: mock_send_message.assert_called_with(ANY, contains("Categorias:"))
        pass # Placeholder for full implementation

    # Outros testes para a máquina de estados da view whatsapp_webhook:
    # - test_webhook_opcao_2_falar_atendente
    # - test_webhook_escolha_categoria_valida
    # - test_webhook_escolha_categoria_invalida
    # - test_webhook_escolha_produto_valido
    # - test_webhook_adicionar_ao_carrinho_e_continuar
    # - test_webhook_finalizar_pedido_carrinho_vazio
    # - test_webhook_finalizar_pedido_com_itens
    # - test_webhook_confirmar_pedido_pix
    # - test_webhook_cancelar_pedido
    # - test_webhook_enviar_pago
    # - test_webhook_conversa_em_estado_transferido
    # - test_webhook_palavra_chave_cancelar_global
    # Cada teste simularia a mensagem do usuário ('Body') e o número ('From'),
    # verificaria o status da resposta HTTP, o estado_conversa no BD,
    # e a mensagem enviada de volta (usando o mock de send_whatsapp_message).

    # Exemplo de como mockar a view diretamente se ela for muito complexa para test client
    # @patch('whatsapp_bot.views.send_whatsapp_message')
    # @patch('your_app.views.PedidoWhatsApp.objects.get_or_create')
    # def test_state_transition_logic_directly(self, mock_get_or_create, mock_send_message):
    #     # Setup mock_pedido_conversa
    #     mock_pedido_conversa = MagicMock(spec=PedidoWhatsApp)
    #     mock_pedido_conversa.estado_conversa = 'INICIO'
    #     mock_get_or_create.return_value = (mock_pedido_conversa, True) # Simula created=True
        
    #     # Call a refactored part of your view or simulate the view call's core logic
    #     # process_incoming_message(from_number, incoming_msg_body) # Hypothetical function
        
    #     # Assertions on mock_pedido_conversa.estado_conversa, mock_pedido_conversa.save.called,
    #     # and mock_send_message.assert_called_with(...)
    #     pass

# Para mais detalhes sobre testes de API com Django REST Framework, veja a documentação do DRF.
# Para testes unitários de lógica de negócios complexa, isole a lógica em funções ou classes
# que podem ser testadas independentemente das views.
```
