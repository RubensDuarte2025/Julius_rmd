# Checklist de Testes Manuais - Frontend MVP

Este checklist cobre os principais fluxos e funcionalidades do frontend para o MVP do sistema Pizzeria SaaS. Deve ser usado para testes exploratórios e para garantir que os requisitos básicos foram atendidos antes de um deploy ou entrega.

## Configuração Geral Antes de Testar:
- [ ] Backend Pizzeria SaaS está rodando e acessível na URL configurada (ex: `http://localhost:8000/api`).
- [ ] Frontend está rodando em modo de desenvolvimento (`npm run dev`) ou build de produção (`npm run preview`).
- [ ] (Opcional) Abrir o console do navegador (DevTools) para verificar erros de JavaScript ou de rede.
- [ ] (Opcional) Limpar cache do navegador ou usar aba anônima para simular primeiro acesso.

## Módulo de Atendimento Interno (Mesas) - `/atendimento/mesas`

### Dashboard de Mesas (`MesasDashboardPage`):
- [ ] **Listagem de Mesas:**
    - [ ] As mesas são exibidas corretamente com seus números/identificadores?
    - [ ] Os status das mesas (Livre, Ocupada, AguardandoPagamento, Interditada) são refletidos visualmente (ex: cores diferentes)?
    - [ ] A página lida bem com nenhuma mesa cadastrada (exibe mensagem apropriada)?
    - [ ] O botão "Atualizar Lista de Mesas" busca e atualiza a lista de mesas?
    - [ ] Feedback de "Carregando mesas..." é exibido durante a busca?
- [ ] **Navegação:**
    - [ ] Clicar em uma mesa redireciona para a página de operação do pedido daquela mesa (`/atendimento/mesas/:mesaId/pedido`)?

### Página de Operação do Pedido da Mesa (`PedidoMesaOperacaoPage`):
- [ ] **Carregamento/Criação de Pedido:**
    - [ ] Ao acessar a página para uma mesa livre, um novo pedido é implicitamente criado ou a interface permite iniciar um?
    - [ ] Ao acessar a página para uma mesa com pedido 'Aberto' ou 'Fechado', o pedido existente é carregado?
    - [ ] O número da mesa e ID do pedido (se existente) são exibidos?
    - [ ] Feedback de "Carregando dados..." é exibido?
    - [ ] Tratamento de erro se a mesa não existir ou não puder ter pedido aberto (ex: interditada)?
- [ ] **Detalhes do Pedido (`DetalhesPedidoMesa`):**
    - [ ] Se o pedido tem itens, eles são listados corretamente (quantidade, nome, subtotal, observações)?
    - [ ] O total do pedido é calculado e exibido corretamente?
    - [ ] Mensagem de "Nenhum item no pedido ainda" é exibida para pedidos vazios?
- [ ] **Adicionar Itens (`AdicionarItemForm`):**
    - [ ] A lista de produtos é carregada no select/dropdown?
    - [ ] É possível selecionar um produto, definir quantidade e observações?
    - [ ] Ao submeter o formulário, o item é adicionado à lista de "Detalhes do Pedido"?
    - [ ] O total do pedido é atualizado após adicionar um item?
    - [ ] Feedback de sucesso/erro ao adicionar item é exibido?
    - [ ] O formulário é limpo após adicionar um item com sucesso?
    - [ ] Não é possível adicionar itens se o pedido não estiver com status 'Aberto'?
- [ ] **Remover Itens (se implementado no MVP):**
    - [ ] Clicar no botão de remover item pede confirmação?
    - [ ] O item é removido da lista e o total do pedido é atualizado?
- [ ] **Ações do Pedido:**
    - [ ] **Fechar Conta:**
        - [ ] O botão "Fechar Conta" está disponível se o pedido está 'Aberto' e tem itens?
        - [ ] Ao clicar, o status do pedido muda para 'Fechado'?
        - [ ] O modal de "Registrar Pagamento" abre automaticamente (ou um botão para abri-lo se torna proeminente)?
        - [ ] Não é mais possível adicionar/remover itens após fechar a conta?
    - [ ] **Registrar Pagamento (`RegistrarPagamentoForm` no Modal):**
        - [ ] O botão "Registrar Pagamento" está disponível se o pedido está 'Fechado'?
        - [ ] O modal de pagamento abre corretamente?
        - [ ] O valor total do pedido é sugerido no campo "Valor Pago"?
        - [ ] É possível selecionar o método de pagamento?
        - [ ] Ao submeter, o pagamento é registrado? (Verificar no Admin do backend ou se a UI indica sucesso).
        - [ ] A página redireciona para o dashboard de mesas após pagamento bem-sucedido?
        - [ ] Feedback de sucesso/erro é exibido no modal?
        - [ ] O modal pode ser fechado (botão "Cancelar" ou "X")?
- [ ] **Navegação:**
    - [ ] Botão "Voltar para Dashboard de Mesas" funciona?

## Módulo de Cozinha (Pizzaiolo) - `/cozinha` ou `/cozinha/dashboard`

### Painel da Cozinha (`CozinhaDashboardPage`):
- [ ] **Listagem de Pedidos:**
    - [ ] Pedidos de WhatsApp e de Mesa com status_cozinha 'AguardandoPreparo' ou 'EmPreparo' são exibidos como cards?
    - [ ] Os cards exibem as informações corretas (ID, origem, cliente/mesa, horário de entrada, status atual, itens com detalhes)?
    - [ ] A lista é ordenada por horário de entrada (mais antigos primeiro)?
    - [ ] Feedback de "Carregando pedidos..." é exibido?
    - [ ] Mensagem de "Nenhum pedido para preparar" é exibida se a lista estiver vazia?
    - [ ] O botão "Atualizar Lista" busca e atualiza os pedidos?
- [ ] **Interação com Cards de Pedido (`PedidoCozinhaCard`):**
    - [ ] **Marcar Em Preparo:**
        - [ ] Botão disponível para pedidos 'AguardandoPreparo'?
        - [ ] Ao clicar, o status do pedido muda para 'EmPreparo' (refletido no card ou após re-fetch da lista)?
        - [ ] O botão de "Marcar Em Preparo" some e o de "Marcar Pronto" aparece?
    - [ ] **Marcar Pronto:**
        - [ ] Botão disponível para pedidos 'EmPreparo'?
        - [ ] Ao clicar, o status do pedido muda para 'Pronto'?
        - [ ] O card do pedido 'Pronto' some da lista após a atualização (pois a view só busca 'AguardandoPreparo' e 'EmPreparo')?
    - [ ] Feedback de erro se a atualização de status falhar?

## Módulo de Administração - `/admin/...`

*(Assumindo que o usuário está logado como admin ou que as rotas são acessíveis no MVP sem login)*

### Layout Geral (`AdminLayout`, `AdminSidebar`):
- [ ] A barra lateral (`AdminSidebar`) é exibida em todas as páginas do admin?
- [ ] Os links na barra lateral navegam corretamente para as respectivas páginas?
- [ ] O link ativo na barra lateral é destacado?
- [ ] O conteúdo da página é renderizado na área principal (`Outlet` do `AdminLayout`)?

### Dashboard Admin (`AdminDashboardPage`):
- [ ] A página de boas-vindas é exibida?
- [ ] Os links rápidos navegam para as seções corretas?

### Gerenciar Categorias (`GerenciarCategoriasPage`):
- [ ] **Listagem:** Categorias existentes são listadas na tabela?
- [ ] **Criação:**
    - [ ] Modal de "Nova Categoria" abre ao clicar no botão?
    - [ ] É possível preencher nome e descrição e salvar?
    - [ ] A nova categoria aparece na lista após salvar?
    - [ ] Validação de formulário (ex: nome obrigatório) funciona?
- [ ] **Edição:**
    - [ ] Modal de "Editar Categoria" abre com os dados da categoria ao clicar em "Editar"?
    - [ ] É possível alterar os dados e salvar?
    - [ ] A categoria é atualizada na lista?
- [ ] **Exclusão:**
    - [ ] Confirmação é exibida ao clicar em "Excluir"?
    - [ ] A categoria é removida da lista após confirmar?
    - [ ] Tratamento de erro se a categoria não puder ser excluída (ex: produtos associados)?

### Gerenciar Produtos (`GerenciarProdutosPage`):
- [ ] **Listagem:** Produtos existentes são listados (nome, categoria, preço, disponibilidade)?
- [ ] **Criação:**
    - [ ] Modal de "Novo Produto" abre?
    - [ ] O select de categorias é populado corretamente?
    - [ ] Todos os campos do formulário podem ser preenchidos?
    - [ ] O novo produto aparece na lista após salvar?
    - [ ] Validação de formulário (campos obrigatórios) funciona?
- [ ] **Edição:**
    - [ ] Modal de "Editar Produto" abre com os dados corretos?
    - [ ] É possível alterar os dados e salvar?
    - [ ] O produto é atualizado na lista?
- [ ] **Exclusão:**
    - [ ] Confirmação e exclusão funcionam como esperado?

### Gerenciar Mesas (`GerenciarMesasPage`):
- [ ] **Listagem:** Mesas existentes são listadas (número, capacidade, status operacional)?
- [ ] **Criação:** Modal e formulário para nova mesa funcionam?
- [ ] **Edição:** Modal e formulário para editar mesa funcionam?
- [ ] **Exclusão:** Confirmação e exclusão funcionam? (Considerar impacto em pedidos existentes).

### Gerenciar Configurações (`GerenciarConfiguracoesPage`):
- [ ] **Listagem:** Configurações (chave, valor, descrição) são listadas?
- [ ] **Edição:**
    - [ ] Modal de "Editar Configuração" abre com os dados corretos (chave não editável)?
    - [ ] É possível alterar o valor e salvar?
    - [ ] A configuração é atualizada na lista?
    - [ ] (Não é esperado criar/excluir chaves via UI no MVP).

### Relatório de Vendas (`RelatorioVendasPage`):
- [ ] **Filtros de Data:** É possível selecionar data de início e fim?
- [ ] **Gerar Relatório:** Ao clicar, a tabela é populada com dados de pagamentos aprovados no período?
- [ ] **Dados da Tabela:** Colunas (ID Pag., ID Pedido, Origem, Data, Valor, Método) são exibidas corretamente?
- [ ] **Total de Vendas:** O total de vendas no período é calculado e exibido?
- [ ] Tratamento se não houver vendas no período?

### Relatório de Produtos Vendidos (`RelatorioProdutosPage`):
- [ ] **Filtros de Data:** Funcionam como no relatório de vendas?
- [ ] **Gerar Relatório:** Tabela é populada com produtos e quantidade total vendida no período?
- [ ] **Dados da Tabela:** Colunas (Nome Produto, Quantidade Vendida) são exibidas?
- [ ] Ordenação (ex: mais vendidos primeiro) funciona?
- [ ] Tratamento se não houver produtos vendidos no período?

## Testes Gerais de Usabilidade (Aplicável a todas as telas)
- [ ] **Consistência Visual:** A aparência geral (cores, fontes, espaçamento) é razoavelmente consistente? (Considerando o tema MUI básico).
- [ ] **Feedback de Ações:** O usuário recebe feedback ao clicar em botões ou realizar ações (ex: "Salvando...", "Erro ao carregar", item adicionado)?
- [ ] **Navegação Intuitiva:** É fácil navegar entre as diferentes seções e voltar?
- [ ] **Tratamento de Erros:** Mensagens de erro são claras e informativas quando algo falha (ex: falha de API, validação de formulário)?
- [ ] **Responsividade Básica:**
    - [ ] A aplicação é minimamente usável em uma tela de tablet (ex: layout não quebra completamente)?
    - [ ] Barras de rolagem aparecem se o conteúdo exceder a tela, em vez de cortar o conteúdo?

Este checklist é um ponto de partida e pode ser expandido conforme o desenvolvimento avança e mais detalhes são definidos.
```
