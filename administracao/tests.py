from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from decimal import Decimal

from .models import ConfiguracaoSistema, ProdutoPlaceholder, CategoriaProdutoPlaceholder
from atendimento_interno.models import Mesa, PedidoMesa, ItemPedidoMesa
from pagamentos.models import Pagamento
from whatsapp_bot.models import PedidoWhatsApp

# Refer to TESTING_STRATEGY.md for overall testing guidelines.

class AdministracaoAPITests(APITestCase):
    def setUp(self):
        # --- Dados para CRUD ---
        self.categoria_admin_teste = CategoriaProdutoPlaceholder.objects.create(nome="Pizzas Admin Test")
        self.produto_admin_teste = ProdutoPlaceholder.objects.create(
            nome="Pizza Admin Produto Teste",
            categoria=self.categoria_admin_teste,
            preco_base=40.00,
            disponivel=True
        )
        self.mesa_admin_teste = Mesa.objects.create(numero_identificador="ADM01", capacidade_default=4)
        self.config_admin_teste = ConfiguracaoSistema.objects.create(
            chave="TESTE_CHAVE_ADMIN",
            valor="Valor Teste Admin",
            descricao="Configuração de teste para API Admin"
        )

        # --- Dados para Relatórios ---
        # Categoria e Produto para itens de pedido
        self.cat_report = CategoriaProdutoPlaceholder.objects.create(nome="Cat Report")
        self.prod_report_1 = ProdutoPlaceholder.objects.create(nome="Prod Report 1", categoria=self.cat_report, preco_base=20.00)
        self.prod_report_2 = ProdutoPlaceholder.objects.create(nome="Prod Report 2", categoria=self.cat_report, preco_base=15.00)

        # PedidoMesa Pago para relatório de vendas e produtos
        self.mesa_report = Mesa.objects.create(numero_identificador="REP01")
        self.pedido_mesa_report = PedidoMesa.objects.create(
            mesa=self.mesa_report, 
            status_pedido=PedidoMesa.STATUS_PAGO,
            data_fechamento=timezone.now() - timezone.timedelta(days=1) # Ontem
        )
        ItemPedidoMesa.objects.create(pedido_mesa=self.pedido_mesa_report, produto=self.prod_report_1, quantidade=2, preco_unitario_no_momento=20.00) # 40.00
        ItemPedidoMesa.objects.create(pedido_mesa=self.pedido_mesa_report, produto=self.prod_report_2, quantidade=1, preco_unitario_no_momento=15.00) # 15.00
        Pagamento.objects.create(pedido=self.pedido_mesa_report, metodo_pagamento=Pagamento.METODO_DINHEIRO, valor_pago=55.00, status_pagamento=Pagamento.STATUS_APROVADO, data_hora_pagamento=self.pedido_mesa_report.data_fechamento)

        # PedidoWhatsApp Pago para relatório de vendas e produtos
        self.pedido_wp_report = PedidoWhatsApp.objects.create(
            telefone_cliente="+5511888887777",
            carrinho_atual=[
                {'id': self.prod_report_1.id, 'nome': self.prod_report_1.nome, 'preco': 20.00, 'quantidade': 3}, # 60.00
                {'id': self.prod_report_2.id, 'nome': self.prod_report_2.nome, 'preco': 15.00, 'quantidade': 1}, # 15.00
            ],
            status_cozinha=PedidoWhatsApp.STATUS_COZINHA_ENTREGUE # Exemplo
        )
        Pagamento.objects.create(pedido=self.pedido_wp_report, metodo_pagamento=Pagamento.METODO_PIX, valor_pago=75.00, status_pagamento=Pagamento.STATUS_APROVADO, data_hora_pagamento=timezone.now() - timezone.timedelta(days=2)) # Anteontem
        
        # Pagamento de outro dia para testar filtro de data
        self.pedido_wp_report_old = PedidoWhatsApp.objects.create(telefone_cliente="+5511888886666", carrinho_atual=[{'id': self.prod_report_1.id, 'nome': self.prod_report_1.nome, 'preco': 20.00, 'quantidade': 1}]) #20
        Pagamento.objects.create(pedido=self.pedido_wp_report_old, metodo_pagamento=Pagamento.METODO_PIX, valor_pago=20.00, status_pagamento=Pagamento.STATUS_APROVADO, data_hora_pagamento=timezone.now() - timezone.timedelta(days=5))


    # --- Testes CRUD (Exemplo para Categoria, similar para Produto, Mesa, Configuracao) ---
    def test_criar_categoria_produto(self):
        url = reverse('administracao:admin-categoria-list') # Basename='admin-categoria'
        data = {'nome': 'Bebidas Admin', 'descricao': 'Refrigerantes e sucos'}
        response = self.client.post(url, data, format='json')
        # self.client.force_authenticate(user=self.admin_user) # Se autenticação for necessária
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CategoriaProdutoPlaceholder.objects.count(), 3 + 1) # 3 do setUp + 1 nova
        self.assertEqual(response.data['nome'], 'Bebidas Admin')

    def test_listar_categorias_produto(self):
        url = reverse('administracao:admin-categoria-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3) # As 3 criadas no setUp (Pizzas Admin Test, Cat Report, e 1 do produto_admin_teste) - ajustar contagem

    def test_detalhar_categoria_produto(self):
        url = reverse('administracao:admin-categoria-detail', kwargs={'pk': self.categoria_admin_teste.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], self.categoria_admin_teste.nome)

    def test_atualizar_categoria_produto(self):
        url = reverse('administracao:admin-categoria-detail', kwargs={'pk': self.categoria_admin_teste.pk})
        data = {'nome': 'Pizzas Especiais Admin', 'descricao': 'Atualizada'}
        response = self.client.patch(url, data, format='json') # PATCH para atualização parcial
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.categoria_admin_teste.refresh_from_db()
        self.assertEqual(self.categoria_admin_teste.nome, 'Pizzas Especiais Admin')

    def test_deletar_categoria_produto(self):
        url = reverse('administracao:admin-categoria-detail', kwargs={'pk': self.categoria_admin_teste.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CategoriaProdutoPlaceholder.objects.filter(pk=self.categoria_admin_teste.pk).exists())

    # --- Testes CRUD para ConfiguracaoSistema (usando 'chave' como lookup) ---
    def test_detalhar_configuracao_sistema_por_chave(self):
        url = reverse('administracao:admin-configuracao-detail', kwargs={'chave': self.config_admin_teste.chave})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['valor'], self.config_admin_teste.valor)

    def test_atualizar_configuracao_sistema_por_chave(self):
        url = reverse('administracao:admin-configuracao-detail', kwargs={'chave': self.config_admin_teste.chave})
        novo_valor = "Novo Valor Teste Admin"
        data = {'valor': novo_valor} # Apenas o valor pode ser atualizado
        response = self.client.put(url, data, format='json') # PUT ou PATCH
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.config_admin_teste.refresh_from_db()
        self.assertEqual(self.config_admin_teste.valor, novo_valor)
        self.assertEqual(response.data['valor'], novo_valor)


    # --- Testes de Relatórios ---
    def test_relatorio_vendas_simples_sem_filtro(self):
        url = reverse('administracao:relatorio_vendas_simples')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Espera 3 pagamentos aprovados do setUp
        self.assertEqual(len(response.data), 3)
        # Verificar ordenação (mais recente primeiro)
        # Pagamento do pedido_mesa_report (ontem) deve ser o primeiro ou segundo,
        # Pagamento do pedido_wp_report (anteontem)
        # Pagamento do pedido_wp_report_old (5 dias atrás)
        # A ordem exata depende de timezone.now() no momento do teste.
        # Vamos verificar os valores totais.
        total_valor_pago = sum(Decimal(p['valor_pago']) for p in response.data)
        self.assertEqual(total_valor_pago, Decimal('55.00') + Decimal('75.00') + Decimal('20.00'))


    def test_relatorio_vendas_simples_com_filtro_data(self):
        # Testar com filtro para pegar apenas o pagamento de self.pedido_mesa_report (ontem)
        data_ontem_str = (timezone.now() - timezone.timedelta(days=1)).strftime('%Y-%m-%d')
        url = f"{reverse('administracao:relatorio_vendas_simples')}?data_inicio={data_ontem_str}&data_fim={data_ontem_str}"
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(Decimal(response.data[0]['valor_pago']), Decimal('55.00'))
        self.assertEqual(response.data[0]['origem_pedido'], 'Mesa')

    def test_relatorio_produtos_vendidos_simples_sem_filtro(self):
        url = reverse('administracao:relatorio_produtos_vendidos_simples')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # prod_report_1: 2 (mesa) + 3 (wp) + 1 (wp_old) = 6
        # prod_report_2: 1 (mesa) + 1 (wp) = 2
        # Espera 2 produtos no relatório
        self.assertEqual(len(response.data), 2) 
        
        dados_prod1 = next(p for p in response.data if p['nome_produto'] == self.prod_report_1.nome)
        dados_prod2 = next(p for p in response.data if p['nome_produto'] == self.prod_report_2.nome)
        
        self.assertEqual(dados_prod1['quantidade_total_vendida'], 6)
        self.assertEqual(dados_prod2['quantidade_total_vendida'], 2)

    def test_relatorio_produtos_vendidos_simples_com_filtro_data(self):
        # Pegar apenas vendas de self.pedido_wp_report_old (5 dias atrás)
        data_5_dias_atras_str = (timezone.now() - timezone.timedelta(days=5)).strftime('%Y-%m-%d')
        url = f"{reverse('administracao:relatorio_produtos_vendidos_simples')}?data_inicio={data_5_dias_atras_str}&data_fim={data_5_dias_atras_str}"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Espera apenas prod_report_1 com quantidade 1
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nome_produto'], self.prod_report_1.nome)
        self.assertEqual(response.data[0]['quantidade_total_vendida'], 1)

    # Testes de Segurança (Esboço):
    # def test_acesso_admin_api_sem_autenticacao(self):
    #     # self.client.logout() # ou self.client.force_authenticate(user=None)
    #     url = reverse('administracao:admin-produto-list')
    #     response = self.client.get(url)
    #     self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    # def test_acesso_admin_api_com_usuario_nao_admin(self):
    #     # user_normal = User.objects.create_user(username='normaluser', password='password')
    #     # self.client.force_authenticate(user=user_normal)
    #     # url = reverse('administracao:admin-produto-list')
    #     # response = self.client.get(url)
    #     # self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) # Se IsAdminUser for usado
    #     pass

    # def test_acesso_admin_api_com_usuario_admin(self):
    #     # admin_user = User.objects.create_superuser(username='adminuser', password='password', email='admin@example.com')
    #     # self.client.force_authenticate(user=admin_user)
    #     # url = reverse('administracao:admin-produto-list')
    #     # response = self.client.get(url)
    #     # self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     pass

# É importante notar que os testes de relatório podem se tornar complexos devido à
# necessidade de mockar ou criar uma quantidade significativa de dados de teste
# para cobrir diferentes cenários de data e combinações de produtos/pedidos.
# Os exemplos acima são simplificações.
#
# Os testes de CRUD para ProdutoPlaceholder, MesaAdmin, e ConfiguracaoSistema
# seguiriam o padrão mostrado para CategoriaProdutoPlaceholder.
```
