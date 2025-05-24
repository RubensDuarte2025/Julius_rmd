# Estratégia de Testes do Frontend (MVP)

Este documento descreve a estratégia de testes e exemplos para o frontend do sistema Pizzeria SaaS (MVP), construído com React e Vite.

## Ferramentas de Teste (Frontend)

*   **Framework de Teste Principal:** **Jest** é uma escolha comum, mas como o projeto usa **Vite**, **Vitest** é a opção recomendada por ser nativamente compatível com Vite, oferecendo uma API similar ao Jest e configuração simplificada. *Para os exemplos, a sintaxe de Jest/Vitest será usada e é largamente intercambiável.*
*   **Biblioteca de Teste de Componentes:** **React Testing Library (RTL)** (`@testing-library/react`) para testar componentes React de uma maneira que se assemelha a como os usuários os utilizam.
*   **Matchers DOM:** **`@testing-library/jest-dom`** para matchers customizados para o DOM (ex: `toBeInTheDocument()`, `toHaveTextContent()`).
*   **Simulação de Eventos de Usuário:** **`@testing-library/user-event`** para simular interações do usuário (cliques, digitação) de forma mais realista.
*   **Mocking de APIs:**
    *   **`jest.mock` / `vi.mock` (Vitest):** Para mockar módulos de serviço (ex: `adminService.js`, `atendimentoService.js`) e suas funções, controlando as respostas das chamadas API durante os testes.
    *   **Mock Service Worker (MSW):** Para um mocking de API mais robusto a nível de rede (Pós-MVP, se necessário). Para o MVP, mockar os módulos de serviço é geralmente suficiente e mais simples.

## Estratégia Geral

*   **Foco no Comportamento do Usuário:** Os testes devem verificar se os componentes e páginas se comportam como o usuário espera, interagindo com eles da mesma forma (buscando por texto visível, roles ARIA, etc.). Evitar testar detalhes internos de implementação.
*   **Testar Componentes Reutilizáveis:** Componentes comuns de UI (`StyledButton`, `StyledModal`, `AdminTable`, etc.) devem ter testes unitários/integração para garantir que são robustos e funcionam como esperado em diferentes cenários (ex: com diferentes props, estados de loading/disabled).
*   **Testar Páginas/Views Principais (Testes de Integração Leves):**
    *   Cobrir os fluxos críticos em cada módulo (Atendimento, Cozinha, Admin).
    *   **Renderização Inicial:** Verificar se a página renderiza corretamente com dados mockados (simulando respostas de API).
    *   **Interações Básicas:** Testar interações do usuário como cliques em botões, preenchimento de formulários simples, navegação (se aplicável dentro da página).
    *   **Chamadas de Serviço:** Verificar se as funções dos serviços API (mockados) são chamadas com os parâmetros corretos quando o usuário interage com a UI.
    *   **Feedback ao Usuário:** Verificar se mensagens de loading, erro e sucesso são exibidas conforme esperado.
*   **Não Focar em Testes E2E com Ferramentas Externas (para MVP):** Testes End-to-End completos com ferramentas como Cypress ou Playwright são valiosos, mas para o MVP, o foco será em testes unitários e de integração com RTL, complementados por testes manuais.

## Organização dos Testes

*   **Localização:** Arquivos de teste devem ter o sufixo `.test.js` ou `.test.jsx` (ex: `StyledButton.test.jsx`, `MesasDashboardPage.test.jsx`).
*   **Colocação:**
    *   Podem ser colocados em uma pasta `__tests__` dentro do diretório do componente/página.
    *   Alternativamente, podem ser colocados ao lado do arquivo do componente (ex: `StyledButton.jsx` e `StyledButton.test.jsx` na mesma pasta). Vite/Vitest/Jest são configuráveis para encontrar arquivos em ambos os locais. Para consistência, podemos adotar uma das abordagens (ex: ao lado do arquivo do componente).

## Configuração do Ambiente de Teste

*   **Vite com Vitest:** Se estiver usando Vitest, a configuração é geralmente mais simples e integrada ao ambiente Vite.
    *   Instalar: `npm install --save-dev vitest @vitest/ui @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom` (jsdom é necessário para simular o ambiente do navegador).
    *   Configurar `vite.config.js` para incluir as configurações de teste do Vitest.
*   **Vite com Jest (Alternativa):**
    *   Instalar: `npm install --save-dev jest @types/jest babel-jest @babel/preset-env @babel/preset-react @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom`
    *   Configurar Jest (`jest.config.js`) e Babel (`babel.config.js`) para transpilar JSX/ES6 e lidar com módulos CSS/assets.
*   **Scripts no `package.json`:** Adicionar scripts para rodar os testes (ex: `"test": "vitest"` ou `"test": "jest"`).

*Para este subtask, assumimos que um ambiente de teste funcional (preferencialmente Vitest com Vite) pode ser configurado seguindo a documentação oficial da ferramenta escolhida.*

## Tipos de Testes e Exemplos de Cenários

Ver exemplos de código em arquivos `.test.jsx` específicos, como:
*   `frontend/src/components/common/StyledButton.test.jsx`
*   `frontend/src/pages/atendimento/MesasDashboardPage.test.jsx`
*   Esqueletos e diretrizes para outras páginas e componentes.

## Testes Manuais/Exploratórios

Além dos testes automatizados, testes manuais são cruciais, especialmente para verificar a usabilidade e fluxos complexos. Uma lista de verificação de exemplo será fornecida em `MANUAL_TESTING_CHECKLIST.md`.

## Medição de Cobertura

*   Ferramentas como Vitest e Jest vêm com opções para gerar relatórios de cobertura de teste.
*   Comando exemplo (Vitest): `vitest run --coverage`
*   Comando exemplo (Jest): `jest --coverage`
*   **Objetivo:** Buscar uma cobertura de testes razoável, focando na qualidade e relevância dos testes para os fluxos críticos do MVP.

Esta estratégia visa garantir a qualidade e a funcionalidade do frontend do sistema Pizzeria SaaS desde o MVP.
```
