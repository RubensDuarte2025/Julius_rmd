# Pizzeria SaaS - Frontend

Este diretório (`frontend`) contém a aplicação frontend para o sistema Pizzeria SaaS, desenvolvida com React e Vite.

## Pré-requisitos

*   Node.js (versão LTS recomendada, verificar compatibilidade com `react-router-dom@7+` que pede Node >=20 - a sandbox atual pode ter uma versão mais antiga, mas o projeto foi criado.)
*   npm (geralmente vem com Node.js)

## Configuração Inicial

1.  **Clone o repositório** (se ainda não o fez).
2.  **Navegue até a pasta do frontend:**
    ```bash
    cd frontend
    ```
3.  **Instale as dependências:**
    ```bash
    npm install
    ```

## Scripts Disponíveis

No diretório do projeto, você pode executar:

### `npm run dev`

Executa a aplicação em modo de desenvolvimento.
Abra [http://localhost:5173](http://localhost:5173) (ou a porta indicada no terminal) para visualizá-la no navegador.

A página será recarregada automaticamente se você fizer edições.
Você também verá quaisquer erros de lint no console.

### `npm run build`

Compila a aplicação para produção na pasta `dist`.
Ele agrupa corretamente o React em modo de produção e otimiza a build para melhor performance.

A build é minificada e os nomes dos arquivos incluem hashes.
Sua aplicação está pronta para ser implantada!

### `npm run lint`

Executa o ESLint para verificar problemas de linting no código.
O Vite já vem com uma configuração básica do ESLint.

### `npm run preview`

Inicia um servidor local para visualizar a build de produção (após executar `npm run build`). Útil para testar a versão final antes do deploy.

## Estrutura de Pastas Principais (`src/`)

*   `assets/`: Imagens, fontes, etc.
*   `components/`: Componentes React reutilizáveis.
    *   `common/`: Componentes genéricos de UI (ex: Button, Modal).
    *   `layout/`: Componentes de layout (ex: Navbar, Sidebar).
*   `constants/`: Arquivos com constantes (ex: `apiEndpoints.js`).
*   `contexts/`: Para gerenciamento de estado global (React Context API).
*   `hooks/`: Custom Hooks React.
*   `pages/`: Componentes que representam as "páginas" da aplicação.
    *   `atendimento/`: Páginas do módulo de atendimento.
    *   `cozinha/`: Páginas do módulo da cozinha.
    *   `admin/`: Páginas do módulo de administração.
    *   `auth/`: Páginas de autenticação (Pós-MVP).
*   `routes/`: Configuração das rotas da aplicação (atualmente em `App.jsx`, pode ser movido para cá).
*   `services/`: Funções para interagir com o backend.
    *   `api.js`: Configuração base do Axios.
*   `styles/`: Arquivos CSS globais, temas (ex: `index.css` já existe).
*   `utils/`: Funções utilitárias genéricas.
*   `App.jsx`: Componente raiz da aplicação, onde as rotas são configuradas.
*   `main.jsx`: Ponto de entrada da aplicação React.

## Backend API

A aplicação frontend espera que o backend Django esteja rodando em `http://localhost:8000`. A URL base da API configurada em `src/services/api.js` é `http://localhost:8000/api`.

Certifique-se de que o backend esteja em execução para que as chamadas de API funcionem.

## Linting e Formatting (Recomendação)

Para manter a qualidade e consistência do código, é altamente recomendado configurar/revisar:
*   **ESLint:** O Vite já inclui uma configuração básica. Pode ser estendida com plugins como `eslint-plugin-react-hooks` (já incluso) e `eslint-plugin-jsx-a11y` para acessibilidade.
*   **Prettier:** Para formatação automática de código.
    *   Instalar: `npm install --save-dev prettier eslint-config-prettier eslint-plugin-prettier`
    *   Criar `.prettierrc.json` na raiz de `frontend/` com suas preferências.
    *   Adicionar `prettier` às extensões e plugins no arquivo de configuração do ESLint (ex: `.eslintrc.cjs`) para que as regras do Prettier sejam aplicadas e não entrem em conflito com o ESLint.

Exemplo `.eslintrc.cjs` (pode variar com a versão do Vite):
```javascript
module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:react/jsx-runtime', // Se estiver usando o novo JSX transform
    'plugin:react-hooks/recommended',
    'plugin:prettier/recommended' // Adiciona Prettier como uma regra ESLint
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parserOptions: { ecmaVersion: 'latest', sourceType: 'module' },
  settings: { react: { version: '18.2' } }, // Ajuste conforme a versão do React
  plugins: ['react-refresh', 'prettier'],
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
    'prettier/prettier': 'error', // Mostra erros do Prettier como erros ESLint
    'react/prop-types': 'off', // Pode ser desabilitado se usando TypeScript ou para MVP
  },
}
```

Exemplo `.prettierrc.json`:
```json
{
  "semi": true,
  "singleQuote": true,
  "jsxSingleQuote": false,
  "trailingComma": "es5",
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false
}
```

## Próximos Passos

*   Desenvolver os componentes de layout (Navbar, Sidebar, etc.).
*   Implementar as rotas e páginas placeholder com conteúdo básico.
*   Conectar com as APIs do backend para buscar e enviar dados.
*   Gerenciar estado da aplicação (Context API ou bibliotecas como Zustand/Redux).
*   Implementar autenticação (Pós-MVP).
```
