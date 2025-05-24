# Pizzeria SaaS - Design da Interface do Usuário (UI) e Experiência do Usuário (UX)

Este documento detalha o design da UI e UX para os diversos componentes do Sistema SaaS da Pizzaria.

## Princípios Gerais de UI/UX

*   **Consistência:** Elementos de design e padrões de interação devem ser consistentes em todas as telas.
*   **Clareza:** Informações e ações devem ser fáceis de entender.
*   **Eficiência:** Permitir que os usuários realizem tarefas rapidamente.
*   **Feedback:** O sistema deve fornecer feedback claro sobre as ações do usuário.
*   **Acessibilidade:** Considerar as necessidades de usuários com diferentes habilidades (ex: contraste de cores, navegação por teclado).
*   **Design Responsivo:** As interfaces web (atendente, cozinha, admin) devem se adaptar a diferentes tamanhos de tela (desktop, tablet).

## 1. Interface do Cliente no WhatsApp (Fluxo de Conversa)

### Fluxo Principal:

1.  **Saudação e Menu Inicial:**
    *   *Bot:* "Olá! Bem-vindo à Pizzaria [Nome da Pizzaria]! Como posso ajudar? 😊"
    *   *Opções (botões/lista numerada):*
        1.  Ver Cardápio e Fazer Pedido 🍕
        2.  Ver Status do Meu Último Pedido status_do_pedido
        3.  Falar com um Atendente 💬
2.  **Ver Cardápio e Fazer Pedido:**
    *   *Bot:* "Ótimo! Aqui estão nossas categorias:"
    *   *Opções (botões/lista):* Pizzas Salgadas, Pizzas Doces, Bebidas, Sobremesas, Voltar ao Menu Principal.
    *   *Ao selecionar categoria (ex: Pizzas Salgadas):*
        *   *Bot:* "Pizzas Salgadas (digite o número para adicionar ao carrinho ou 'V' para voltar):"
        *   *Lista:* "1. Calabresa (M, G) - R$XX, R$YY", "2. Margherita (M, G) - R$XX, R$YY" ...
    *   *Ao selecionar item (ex: "1 G" ou "Calabresa G"):*
        *   *Bot:* "Pizza Calabresa (G) adicionada ao seu carrinho! 🛒 Algo mais ou podemos fechar o pedido?"
        *   *Opções:* Adicionar mais itens, Ver carrinho, Fechar Pedido.
3.  **Ver Carrinho:**
    *   *Bot:* "Seu carrinho: \n1x Pizza Calabresa (G) - R$YY \nTotal: R$YY. "
    *   *Opções:* Continuar comprando, Remover item, Finalizar Pedido.
4.  **Fechar Pedido/Finalizar Pedido:**
    *   *Bot:* "Para finalizar, preciso de algumas informações."
    *   *Coleta de Dados:*
        *   Nome (se não identificado).
        *   Endereço de entrega (se não for retirada) ou opção de "Retirar na Loja".
        *   Confirmação do pedido e valor total.
    *   *Bot:* "Como gostaria de pagar?"
    *   *Opções de Pagamento:* PIX, Cartão de Crédito (link).
5.  **Pagamento PIX:**
    *   *Bot:* "Ótimo! Aqui está o QR Code PIX (imagem) e o código Copia e Cola. Após o pagamento, envie 'PAGO'."
    *   *[Imagem do QR Code]*
    *   `codigo_pix_copia_cola`
6.  **Pagamento Cartão:**
    *   *Bot:* "Clique neste link seguro para pagar com cartão: [link_gateway]". "Após o pagamento, envie 'PAGO'."
7.  **Confirmação de Pagamento (após cliente enviar 'PAGO' e sistema verificar):**
    *   *Bot:* "Pagamento confirmado! 🎉 Seu pedido #[NúmeroDoPedido] está sendo preparado. O tempo estimado é de X minutos."
8.  **Status do Pedido:**
    *   *Cliente digita "status" ou seleciona a opção no menu:*
    *   *Bot:* "Seu pedido #[NúmeroDoPedido] está [Status: Em preparo/Saiu para entrega/Pronto para retirada]."

### Considerações UX para WhatsApp:

*   Usar emojis para tornar a conversa mais amigável e visual.
*   Mensagens curtas, diretas e objetivas.
*   Utilizar botões de resposta rápida (quick replies) e listas de opções sempre que possível para facilitar a interação e evitar erros de digitação.
*   Instruções claras em cada etapa do processo.
*   Oferecer uma opção fácil para "Cancelar" ou "Voltar" em todas as etapas relevantes.
*   Permitir que o usuário digite livremente, mas guiar com opções quando possível.

## 2. Painel de Atendimento Interno (Web - React)

### Tela Principal (Dashboard):

*   **Layout:**
    *   Barra de navegação superior: Logo da Pizzaria, Nome do Atendente logado, Botão de Logout.
    *   Área principal: Visualização do mapa de mesas.
    *   Barra lateral (opcional, pode ser recolhível): Ações rápidas como "Novo Pedido para Viagem", "Lista de Espera de Clientes".
*   **Mapa de Mesas:**
    *   Representação gráfica das mesas (quadrados/círculos com número da mesa).
    *   Cores indicando status:
        *   Verde: Livre
        *   Amarelo/Laranja: Ocupada
        *   Vermelho: Aguardando Pagamento/Fechamento de Conta
        *   Cinza: Interditada/Indisponível
    *   Informações exibidas em cada mesa (ao passar o mouse/tooltip ou em texto pequeno dentro do elemento da mesa): Número da Mesa, Horário de Abertura da Comanda, Valor Parcial do Pedido.
    *   **Ação:** Clique em uma mesa para abrir a tela de detalhes/lançar pedido para aquela mesa.

### Tela de Pedido da Mesa (Pode ser um modal sobre o mapa de mesas ou uma nova seção/página):

*   **Cabeçalho:** Número da Mesa, Número do Pedido (se já existir), Nome do Cliente (opcional, pode ser adicionado).
*   **Layout em Colunas/Seções:**
    *   **Coluna 1 (Cardápio Interativo):**
        *   Tabs ou Dropdown para filtrar por Categorias (Pizzas, Bebidas, Sobremesas, etc.).
        *   Lista de produtos da categoria selecionada: Nome do Produto, Preço.
        *   Botão "+" ou "Adicionar" ao lado de cada produto.
        *   Campo de busca de produtos dentro do cardápio.
        *   Ao clicar em um produto, pode abrir um sub-modal para customizações (ex: tamanho, ingredientes extras/removidos, observações do item).
    *   **Coluna 2 (Itens do Pedido Atual):**
        *   Lista de itens já adicionados ao pedido: Quantidade (com botões +/- para alterar), Nome do Produto, Preço Unitário, Subtotal do item.
        *   Opção de remover item ou editar observações específicas do item.
        *   Campo para "Observações Gerais do Pedido".
    *   **Coluna 3 (Resumo e Ações):**
        *   Subtotal do pedido.
        *   Taxa de Serviço (se configurada e aplicável, com opção de remover).
        *   Total a pagar.
        *   Botões de Ação:
            *   "Enviar para Cozinha" (confirma os itens e envia para preparo).
            *   "Salvar Pedido" (salva o estado atual sem enviar para cozinha, para mesas que continuam consumindo).
            *   "Imprimir Conta Parcial" (para conferência do cliente).
            *   "Fechar Conta / Iniciar Pagamento".

### Tela de Pagamento (Modal sobre a tela de pedido da mesa):

*   Exibição clara do valor total.
*   Opções de método de pagamento: Dinheiro, Cartão (Maquineta), PIX (Maquineta ou QR Code gerado).
*   Se Dinheiro: Campo para "Valor Recebido", sistema calcula e exibe o "Troco".
*   Se Cartão/PIX (via maquineta): Botão "Confirmar Pagamento Recebido".
*   Se PIX (QR Code gerado no sistema): Exibir QR Code e opção de copiar código.
*   Botão "Finalizar Pedido e Liberar Mesa" (após confirmação do pagamento).

### Considerações UX para Atendente:

*   Interface otimizada para uso em tablets, com botões grandes e áreas de toque responsivas (touch-friendly).
*   Fluxo de lançamento de itens deve ser rápido e intuitivo, minimizando cliques.
*   Alertas visuais ou sonoros discretos para pedidos prontos na cozinha que precisam ser entregues à mesa.
*   Busca eficiente no cardápio.

## 3. Painel do Administrador (Web - React)

### Layout Geral:

*   Barra de navegação lateral persistente: Dashboard, Gerenciamento de Cardápio (Produtos, Categorias, Ingredientes), Gerenciamento de Mesas, Gerenciamento de Usuários, Relatórios, Configurações do Sistema.
*   Área de conteúdo principal à direita da navegação.

### Dashboard (Tela Inicial do Admin):

*   Visão geral com indicadores chave: Total de vendas (dia/semana/mês), número de pedidos, ticket médio, mesas mais movimentadas.
*   Gráficos simples e informativos (ex: vendas ao longo da semana, produtos mais vendidos).

### Gerenciamento de Cardápio:

*   **Produtos:**
    *   Listagem de produtos com filtros (por categoria) e campo de busca.
    *   Colunas da tabela: Foto (thumbnail), Nome, Categoria, Preço Base, Disponível (toggle switch).
    *   Ações por item: Editar, Remover. Botão "Adicionar Novo Produto".
    *   Formulário de Produto (em modal ou nova página):
        *   Campos: Nome, Descrição, Categoria (seleção), Preço Base, Upload de Foto.
        *   Seção para Ingredientes (se permitir visualização/customização básica).
        *   Tempo de preparo estimado.
        *   Opção de "Disponível".
*   **Categorias:** CRUD para categorias de produtos.
*   **Ingredientes:** CRUD para ingredientes (usado em customizações e ficha técnica).

### Gerenciamento de Mesas:

*   Listagem de mesas: Número da Mesa, Status Atual (informativo, não interativo como no painel do atendente), Capacidade.
*   Ações: Adicionar Nova Mesa (definir número e capacidade), Editar, Marcar como Interditada/Liberar.

### Relatórios:

*   Interface para selecionar tipo de relatório (Vendas, Produtos, Clientes, etc.) e período de tempo.
*   Exibição dos dados em tabelas paginadas e gráficos interativos.
*   Opção de exportar relatórios (CSV, PDF).

### Configurações do Sistema:

*   Formulários agrupados por seções:
    *   Dados da Pizzaria: Nome, Endereço, Telefone, CNPJ.
    *   Taxas: Taxa de serviço (percentual), taxa de entrega (fixa ou por área - simplificado para MVP).
    *   Horários de Funcionamento.
    *   Integrações: Chaves de API para WhatsApp BSP, Gateways de Pagamento.
    *   Mensagens padrão (WhatsApp).

### Considerações UX para Admin:

*   Clareza na apresentação de dados e estatísticas.
*   Facilidade para encontrar informações e realizar configurações críticas.
*   Controles de formulário intuitivos com validação clara.
*   Performance na carga de relatórios e listas grandes.

## 4. Tela do Pizzaiolo / Cozinha (Web - React)

### Layout (Kanban ou Lista Cronológica):

*   **Opção 1: Kanban (Preferencial para visualização de fluxo):**
    *   Colunas: "Novos Pedidos" (Aguardando Preparo), "Em Preparo", "Prontos" (Aguardando Retirada/Entrega).
    *   Cards de Pedido: Movidos entre as colunas via drag-and-drop ou botões de ação no card.
*   **Opção 2: Lista Cronológica:**
    *   Pedidos são listados em ordem de chegada (ou prioridade). Status é indicado por cor de fundo do card/tag. Menos visual para o fluxo, mas pode ser mais simples.

### Card de Pedido (Elemento principal da tela):

*   **Informações Claras e Destacadas:**
    *   Número do Pedido ou Número da Mesa (bem visível).
    *   Tipo: "MESA" ou "WHATSAPP (Entrega)" ou "WHATSAPP (Retirada)".
    *   Horário do Pedido (e tempo decorrido desde o pedido).
    *   Lista de Itens do Pedido:
        *   Quantidade.
        *   Nome do Produto (ex: Pizza Calabresa G).
        *   Observações importantes do item (ex: "SEM CEBOLA", "METADE MUSSARELA / METADE CALABRESA", "BORDA RECHEADA").
*   **Ações no Card:**
    *   Botão: "Iniciar Preparo" (move para "Em Preparo").
    *   Botão: "Marcar como Pronto" (move para "Prontos").

### Alertas e Notificações:

*   Alertas sonoros e/ou visuais configuráveis para a chegada de novos pedidos.
*   Destaque visual para pedidos que estão se aproximando do tempo limite de preparo ou que estão atrasados (baseado no tempo estimado do produto e tempo configurado).

### Considerações UX para Pizzaiolo/Cozinha:

*   Alta legibilidade: Fontes grandes, bom contraste, informações essenciais visíveis sem necessidade de cliques extras (especialmente em um ambiente de cozinha movimentado e possivelmente à distância).
*   Interação mínima e rápida: Ideal para uso em tablets montados na parede, com interface touch-friendly.
*   Resistente a ambiente de cozinha (se for um dispositivo de hardware dedicado, a interface deve ser simples para não sobrecarregar).
*   Feedback visual claro ao mudar o status de um pedido.

## Interatividade (Arrastar Elementos)

*   A funcionalidade de "telas que possam ser movidas pelo mouse do cursor" pode ser interpretada e aplicada das seguintes formas:
    *   **Janelas/Modais Arrastáveis:** Em algumas interfaces web mais densas (como o Painel do Administrador ou, em certos casos, o Painel de Atendimento), modais ou painéis de informação secundários poderiam ser arrastáveis. Isso permitiria ao usuário organizar a visualização de múltiplas informações simultaneamente.
        *   *Implementação:* Usar bibliotecas como `react-draggable` para componentes React.
        *   *Consideração:* Avaliar a real necessidade para não adicionar complexidade desnecessária. Para o MVP, pode ser um "nice-to-have".
    *   **Elementos Kanban Arrastáveis:** Conforme descrito para a Tela do Pizzaiolo (Cozinha), onde os cards de pedido são arrastados entre colunas que representam diferentes estágios de preparo ("Novos Pedidos", "Em Preparo", "Prontos"). Esta é uma aplicação primária e muito útil da interatividade de arrastar.
        *   *Implementação:* Bibliotecas como `react-beautiful-dnd` ou similares para criar colunas Kanban interativas.

Este detalhamento de UI/UX servirá como guia fundamental para os desenvolvedores frontend e designers na criação dos wireframes visuais, protótipos clicáveis e, subsequentemente, no desenvolvimento das interfaces finais.
