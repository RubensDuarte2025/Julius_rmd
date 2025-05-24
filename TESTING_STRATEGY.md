# Estratégia de Testes do Backend (MVP)

Este documento descreve a estratégia de testes e exemplos para o backend do sistema Pizzeria SaaS (MVP).

## Ferramentas de Teste (Django)

*   **Framework de Teste Principal:** `unittest` do Django (baseado no `unittest` do Python).
*   **Testes de API:** `APIRequestFactory` e `APITestCase` do Django REST Framework.
*   **Mocking:** `unittest.mock.patch` e objetos mock.
*   **Cobertura de Teste:** `Coverage.py` para medir a porcentagem de código coberto por testes.

## Estratégia Geral

A estratégia de testes é dividida em duas categorias principais: Testes Unitários e Testes de Integração/API.

*   **Testes Unitários:**
    *   **Foco:** Isolar e testar pequenas unidades de código, como funções individuais, métodos de modelos, lógica de services, e componentes de formulários (se aplicável).
    *   **Objetivo:** Verificar a correção da lógica interna de cada componente.
    *   **Características:** Rápidos de executar, não dependem de componentes externos como banco de dados (quando possível, usando mocks) ou APIs de terceiros.

*   **Testes de Integração/API:**
    *   **Foco:** Testar a interação entre diferentes componentes do sistema, especialmente as views da API (ViewSets DRF).
    *   **Objetivo:** Garantir que os endpoints da API se comportem conforme o esperado, incluindo a correta manipulação de requisições, interações com a base de dados (modelos), execução de lógica de negócios (services), e formatação das respostas.
    *   **Características:** Mais lentos que testes unitários, pois envolvem o ciclo de requisição/resposta HTTP e, frequentemente, interações com o banco de dados de teste.

*   **Organização dos Testes:**
    *   Cada app Django (`whatsapp_bot`, `atendimento_interno`, `cozinha_api`, `pagamentos`, `administracao`) terá seu próprio arquivo `tests.py`.
    *   Para apps com um grande número de testes, o arquivo `tests.py` pode ser convertido em um diretório `tests/` contendo múltiplos arquivos de teste (ex: `test_models.py`, `test_views.py`, `test_services.py`).

## Tipos de Testes e Exemplos de Cenários

### 1. Testes Unitários

*   **`pagamentos.services.registrar_pagamento_para_pedido` (`pagamentos/tests.py`):**
    *   Verificar se um objeto `Pagamento` é criado corretamente com os dados fornecidos.
    *   Testar a criação de pagamentos para diferentes tipos de pedidos (mock de `PedidoWhatsApp`, mock de `PedidoMesa`).
    *   Verificar se os campos default (ex: `status_pagamento`, `data_hora_pagamento`) são aplicados corretamente.
    *   Testar com diferentes métodos de pagamento.
    *   (Pós-MVP ou se a lógica for movida para o service) Verificar se o status do pedido associado é atualizado, caso essa lógica seja centralizada no service.

*   **Lógica da máquina de estados em `whatsapp_bot.views.whatsapp_webhook` (`whatsapp_bot/tests.py`):**
    *   Para cada estado da conversa, simular diferentes entradas do usuário (válidas e inválidas).
    *   Verificar se o `estado_conversa` no modelo `PedidoWhatsApp` é atualizado corretamente.
    *   Verificar se a mensagem de resposta do bot (simulada via `send_whatsapp_message`) é a esperada para cada cenário.
    *   Utilizar `unittest.mock.patch` para mockar `send_whatsapp_message` e `timezone.now` (se necessário para controlar o tempo).

*   **Métodos do modelo `PedidoWhatsApp` (`whatsapp_bot/tests.py`):**
    *   Testar `adicionar_item_carrinho`: verificar adição de novo item, atualização de quantidade de item existente.
    *   Testar `remover_ultimo_item_carrinho`: verificar remoção e comportamento com carrinho vazio.
    *   Testar `calcular_total_carrinho`: verificar cálculo correto com diferentes itens e quantidades.
    *   Testar `reset_conversa`: verificar se o estado e o carrinho são reiniciados.

*   **Métodos de modelos em `atendimento_interno` (`atendimento_interno/tests.py`):**
    *   Testar `PedidoMesa.calcular_total()`: verificar cálculo correto.
    *   Testar qualquer outra lógica customizada nos modelos `Mesa` ou `ItemPedidoMesa`.

*   **Lógica de agregação em relatórios (`administracao/tests.py`):**
    *   Criar dados de teste (mock de `Pagamento`, `ItemPedidoMesa`, `PedidoWhatsApp` com carrinhos).
    *   Chamar a lógica de agregação diretamente (se estiver em funções/métodos separáveis) ou através da view do relatório em modo unitário (se possível, mockando o request).
    *   Verificar se os totais e agrupamentos estão corretos.

### 2. Testes de Integração/API (usando `APITestCase`)

Estes testes verificam os endpoints da API de ponta a ponta (dentro do contexto do Django).

*   **APIs de `atendimento_interno` (`atendimento_interno/tests.py`):**
    *   **Criar Pedido para Mesa:** `POST /api/mesas/{mesa_id}/pedidos/`
        *   Verificar status code 201.
        *   Verificar se `PedidoMesa` foi criado e associado à mesa correta.
        *   Verificar se o status da mesa foi atualizado para 'Ocupada'.
    *   **Adicionar Item ao Pedido:** `POST /api/pedidos_mesa/{pedido_id}/itens/`
        *   Verificar status code 201.
        *   Verificar se `ItemPedidoMesa` foi criado e associado ao pedido.
        *   Verificar se `status_cozinha` do `PedidoMesa` foi para `AguardandoPreparo`.
    *   **Registrar Pagamento:** `POST /api/pedidos_mesa/{pedido_id}/registrar-pagamento/`
        *   Verificar status code 200.
        *   Verificar se `PedidoMesa.status_pedido` é 'Pago'.
        *   Verificar se `Mesa.status` é 'Livre'.
        *   Verificar se um registro `Pagamento` foi criado.
    *   **Listar Mesas:** `GET /api/mesas/`
        *   Verificar status code 200 e estrutura dos dados.
    *   **Atualizar Status da Mesa:** `PATCH /api/mesas/{mesa_id}/atualizar-status/`
        *   Verificar status code 200 e se o status da mesa foi alterado.

*   **APIs de `cozinha_api` (`cozinha_api/tests.py`):**
    *   **Listar Pedidos para Preparar:** `GET /api/cozinha/pedidos_para_preparar/`
        *   Criar `PedidoWhatsApp` e `PedidoMesa` com `status_cozinha` apropriado.
        *   Chamar API e verificar se ambos aparecem na lista, com dados formatados corretamente.
        *   Verificar ordenação por `horario_entrada_cozinha`.
    *   **Atualizar Status do Pedido na Cozinha:** `PATCH /api/cozinha/pedidos/{tipo_origem}/{id_pedido_origem}/status/`
        *   Criar um pedido (`PedidoWhatsApp` ou `PedidoMesa`).
        *   Chamar API para mudar `status_cozinha` para `EmPreparo`, verificar a mudança no modelo.
        *   Chamar API para mudar `status_cozinha` para `Pronto`, verificar a mudança no modelo.
        *   Testar transições de status inválidas.

*   **APIs de `pagamentos` (`pagamentos/tests.py`):**
    *   **Listar Pagamentos por Pedido:** `GET /api/pagamentos/pedido/{tipo_origem}/{id_pedido_origem}/`
        *   Criar um pedido (`PedidoWhatsApp` ou `PedidoMesa`).
        *   Criar múltiplos registros `Pagamento` associados a este pedido.
        *   Chamar API e verificar se todos os pagamentos corretos são listados.
        *   Testar com pedido sem pagamentos.
        *   Testar com `tipo_origem` ou `id_pedido_origem` inválidos.

*   **APIs de `administracao` (`administracao/tests.py`):**
    *   **CRUD para `ProdutoPlaceholder`, `CategoriaProdutoPlaceholder`, `Mesa`, `ConfiguracaoSistema`:**
        *   Para `POST`: verificar criação, status 201, e dados retornados.
        *   Para `GET` (lista e detalhe): verificar status 200 e estrutura dos dados.
        *   Para `PUT/PATCH`: verificar atualização, status 200, e dados atualizados no BD.
        *   Para `DELETE`: verificar remoção, status 204, e ausência no BD.
        *   Para `ConfiguracaoSistema`, testar lookup por `chave`.
    *   **APIs de Relatórios (`VendasSimplesRelatorioView`, `ProdutosVendidosSimplesRelatorioView`):**
        *   Popular dados de teste (pedidos, pagamentos, itens de diferentes tipos e datas).
        *   Chamar as APIs com e sem filtros de data (`data_inicio`, `data_fim`).
        *   Verificar se os dados agregados e filtrados retornados estão corretos e se a estrutura do JSON de resposta está correta.

### 3. Testes de Segurança (Considerações)

Incorporar testes de segurança nas suítes de testes de API, especialmente para endpoints administrativos ou que manipulam dados sensíveis.
*   **Autenticação:**
    *   Tentar acessar endpoints protegidos sem autenticação (esperar 401 Unauthorized ou 403 Forbidden, dependendo da configuração).
*   **Autorização (Permissões):**
    *   Se permissões como `IsAdminUser` forem implementadas:
        *   Acessar endpoints de admin com um usuário não-admin (esperar 403 Forbidden).
        *   Acessar com usuário admin (esperar sucesso: 200, 201, 204).
*   **Validação de Entrada:**
    *   Testar endpoints com dados maliciosos ou inesperados para garantir que a validação (serializers, views) os rejeite corretamente (esperar 400 Bad Request).

## Execução dos Testes

*   **Comando para rodar todos os testes:** `python manage.py test`
*   **Rodar testes de um app específico:** `python manage.py test nome_do_app`
*   **Rodar uma classe de teste específica:** `python manage.py test nome_do_app.NomeDaClasseDeTeste`
*   **Rodar um método de teste específico:** `python manage.py test nome_do_app.NomeDaClasseDeTeste.nome_do_metodo_de_teste`

## Medição de Cobertura

*   **Comandos:**
    ```bash
    coverage run manage.py test
    coverage report
    coverage html  # Para um relatório HTML detalhado
    ```
*   **Objetivo:** Buscar uma alta cobertura de testes, mas priorizar a qualidade e relevância dos testes sobre a porcentagem pura.

## Documentação Adicional

*   Manter um arquivo `TESTING.md` (este arquivo) na raiz do projeto, descrevendo a estratégia e os principais cenários de teste.
*   Comentar os testes de forma clara para explicar o que está sendo testado e por quê.

Esta estratégia visa garantir a robustez e a qualidade do backend do sistema Pizzeria SaaS desde o MVP.
```
