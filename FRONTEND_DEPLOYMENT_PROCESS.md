# Processo de Build e Preparação para Implantação do Frontend (React)

Este documento detalha o processo de build e as estratégias de implantação para o frontend da aplicação Pizzeria SaaS, construído com React e Vite.

## 1. Gerar o Build Estático

O primeiro passo é gerar os arquivos estáticos otimizados da aplicação frontend.

*   **Comando (usando Vite):**
    *   Navegue até a raiz do projeto frontend (`frontend/`).
    *   Execute o comando de build:
        ```bash
        npm run build
        ```
    *   Este comando criará uma pasta `dist/` (por padrão no Vite). Esta pasta conterá todos os arquivos estáticos necessários para a implantação:
        *   `index.html`: O ponto de entrada da aplicação.
        *   Assets: Arquivos JavaScript (transpilados e agrupados), CSS (minificados), imagens e fontes. Estes arquivos geralmente têm nomes hasheados para facilitar o cache busting.

*   **Verificar o Build (Localmente):**
    *   Após a conclusão do build, é uma boa prática testar se os arquivos estáticos gerados funcionam corretamente. O Vite oferece um comando para servir localmente o conteúdo da pasta `dist/`:
        ```bash
        npm run preview
        ```
    *   Este comando iniciará um servidor local simples. Acesse o endereço fornecido no terminal (geralmente `http://localhost:4173` ou similar) para verificar a aplicação em sua forma de produção.

## 2. Estratégias de Implantação e Configurações

Existem várias estratégias para implantar o frontend React. A escolha depende da infraestrutura existente, requisitos de performance, escalabilidade e complexidade.

### Estratégia A: Servir o Frontend com Nginx (Junto ao Backend Django)

Esta estratégia é adequada se o backend Django já está sendo servido via Gunicorn e Nginx.

*   **Pré-requisitos:**
    *   Backend Django implantado e funcionando com Gunicorn (ou outro ASGI/WSGI server) e Nginx como proxy reverso.

*   **Passos:**
    1.  **Copiar os Arquivos do Build:**
        *   Transfira todo o conteúdo da pasta `frontend/dist/` para o servidor de produção.
        *   O local de destino deve ser acessível pelo Nginx (ex: `/var/www/pizzaria_frontend/`).
    2.  **Configurar o Nginx:**
        *   Edite o arquivo de configuração do Nginx para o seu site (ex: `/etc/nginx/sites-available/suapizzaria.com`).
        *   **Servir API Backend:** Mantenha a configuração existente do `location` para a API (ex: `/api/`) que faz o proxy reverso para o Gunicorn/Django.
        *   **Servir Assets Estáticos do Frontend:** Adicione um `location` específico para os assets gerados pelo Vite (ex: `/assets/`, ou os subdiretórios como `/js/`, `/css/` se o Vite os organizar assim). Configure cabeçalhos de cache longos para esses arquivos, pois eles têm nomes hasheados.
        *   **Servir `index.html` (Rota Raiz):** Adicione um `location /` que sirva o `index.html` da pasta do frontend. É crucial usar `try_files $uri $uri/ /index.html;` para que todas as rotas definidas no React Router funcionem corretamente, mesmo ao acessar URLs diretamente ou ao dar refresh na página.

    *   **Exemplo de Configuração Nginx (simplificado):**
        ```nginx
        server {
            listen 80;
            server_name suapizzaria.com; # Substitua pelo seu domínio

            # Localização para a API do Django
            location /api/ {
                proxy_pass http://localhost:8000; # Ou o endereço do socket do Gunicorn
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
            }

            # Localização para os assets estáticos do frontend
            # O Vite pode colocar os assets em uma subpasta como 'assets' dentro de 'dist/'
            location /assets/ { 
                alias /var/www/pizzaria_frontend/assets/; # Caminho no servidor para os assets
                try_files $uri $uri/ =404;
                expires 1y; # Cache longo para assets com hash
                add_header Cache-Control "public";
            }

            # Localização raiz para servir o index.html e permitir o roteamento do React
            location / {
                root /var/www/pizzaria_frontend; # Pasta onde o conteúdo de 'dist/' foi copiado
                try_files $uri $uri/ /index.html; # Importante para o React Router
            }

            # Configurações adicionais: SSL (HTTPS), logs, etc.
            # Exemplo para HTTPS (requer certificado SSL):
            # listen 443 ssl;
            # ssl_certificate /etc/letsencrypt/live/suapizzaria.com/fullchain.pem;
            # ssl_certificate_key /etc/letsencrypt/live/suapizzaria.com/privkey.pem;
            # include /etc/letsencrypt/options-ssl-nginx.conf; # Configurações de SSL recomendadas
            # ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # Parâmetro DH
        }
        ```

*   **Vantagens:**
    *   Gerenciamento de um único servidor.
    *   Configuração de CORS (Cross-Origin Resource Sharing) mais simples, pois frontend e backend podem ser servidos da mesma origem.
*   **Desvantagens:**
    *   Maior acoplamento entre frontend e backend no mesmo servidor.

### Estratégia B: Servir com Django (Menos Comum para React Puro)

Servir uma aplicação React complexa diretamente pelo Django, mesmo com ferramentas como WhiteNoise para arquivos estáticos, geralmente não é a abordagem mais performática ou flexível em comparação com Nginx ou serviços de hospedagem de estáticos dedicados. O Django é primariamente otimizado para servir templates dinâmicos e APIs.

*   Se esta abordagem fosse escolhida:
    1.  O `index.html` gerado pelo Vite precisaria ser adaptado para ser um template do Django.
    2.  Os assets estáticos do frontend (JS, CSS) seriam coletados pelo `collectstatic` do Django e servidos pelo WhiteNoise (em produção) ou pelo servidor de desenvolvimento do Django.
    3.  O Django precisaria ser configurado para servir o template `index.html` para todas as rotas do frontend.

### Estratégia C: Serviço de Hospedagem de Sites Estáticos (Ex: AWS S3 + CloudFront, Netlify, Vercel, GitHub Pages)

Esta é uma abordagem moderna e robusta, especialmente para aplicações React.

*   **Passos (Exemplo com AWS S3 + CloudFront):**
    1.  **Fazer Upload dos Arquivos:** Envie todo o conteúdo da pasta `frontend/dist/` para um bucket AWS S3.
    2.  **Configurar o Bucket S3:** Configure o bucket para hospedagem de site estático, definindo `index.html` como o documento de índice e, opcionalmente, como o documento de erro.
    3.  **Configurar CloudFront (CDN):**
        *   Crie uma distribuição CloudFront e configure a origem para apontar para o endpoint do site estático do seu bucket S3 (não o endpoint da API do S3).
        *   Configure HTTPS usando um certificado SSL do AWS Certificate Manager (ACM).
        *   **Tratamento de Erros para SPA:** Configure as "Error Pages" (Páginas de Erro Personalizadas) no CloudFront. Para erros 403 (Forbidden) e 404 (Not Found) do S3, redirecione para `/index.html` com um código de resposta HTTP 200. Isso é crucial para que o roteamento do React (react-router-dom) funcione corretamente em sub-rotas ao dar refresh ou acessar URLs diretamente.
        *   Configure o comportamento de cache (TTLs) para os arquivos. Assets com hash podem ter TTLs longos, enquanto `index.html` pode ter um TTL mais curto ou ser invalidado em cada deploy.
    4.  **Configurar CORS no Backend Django:**
        *   Como o frontend (servido via CloudFront/S3) estará em um domínio diferente da API backend, é **obrigatório** configurar o CORS no Django.
        *   Utilize a biblioteca `django-cors-headers`.
        *   No `settings.py` do Django, adicione o domínio do frontend (CloudFront) à lista de origens permitidas:
            ```python
            # settings.py
            INSTALLED_APPS = [
                # ...
                'corsheaders',
                # ...
            ]

            MIDDLEWARE = [
                'corsheaders.middleware.CorsMiddleware', # Geralmente no topo ou antes de CommonMiddleware
                # ...
            ]

            CORS_ALLOWED_ORIGINS = [
                "https_dominio_do_seu_frontend_cloudfront.net", # Ex: https://d123xyz.cloudfront.net
                # Para desenvolvimento local, se o frontend roda em uma porta diferente do backend:
                # "http://localhost:5173", # Porta padrão do Vite dev server
            ]
            # Ou, para maior flexibilidade com subdomínios (cuidado em produção):
            # CORS_ALLOWED_ORIGIN_REGEXES = [
            #     r"^https://\w+\.suapizzaria\.com$",
            # ]
            # Para MVP, se o domínio for fixo, CORS_ALLOWED_ORIGINS é mais seguro.
            # CORS_ALLOW_ALL_ORIGINS = True # Apenas para testes, NUNCA em produção.
            ```

*   **Vantagens:**
    *   Alta escalabilidade e disponibilidade.
    *   Excelente performance devido ao uso de CDN para servir os assets próximos aos usuários.
    *   Desacoplamento total da infraestrutura do backend.
*   **Desvantagens:**
    *   Configuração de CORS é obrigatória e pode ser um ponto de atenção.
    *   Pode envolver um pouco mais de complexidade inicial na configuração da AWS (S3, CloudFront, ACM).

## 3. Variáveis de Ambiente no Frontend

Aplicações React frequentemente precisam de variáveis de ambiente configuradas durante o processo de build (não em tempo de execução no cliente, pois são arquivos estáticos). O Vite lida com isso usando arquivos `.env`.

*   Crie arquivos `.env` na raiz do projeto `frontend/` (ex: `.env`, `.env.production`).
*   As variáveis devem ser prefixadas com `VITE_`. Exemplo:
    ```env
    # .env ou .env.production
    VITE_API_BASE_URL=https_api.suapizzaria.com/api
    VITE_GOOGLE_MAPS_API_KEY=SUA_CHAVE_PUBLICA_AQUI # Exemplo de chave pública
    ```
*   No código da aplicação React, acesse essas variáveis usando `import.meta.env`:
    ```javascript
    const apiUrl = import.meta.env.VITE_API_BASE_URL;
    // console.log(apiUrl);
    ```
*   **Importante:** Somente variáveis prefixadas com `VITE_` são expostas ao código do cliente. Não inclua segredos (chaves de API privadas, senhas) nesses arquivos, pois eles serão embutidos nos arquivos JavaScript do build. A URL da API é um caso de uso comum e seguro para esta funcionalidade.

## 4. Considerações Finais

*   **HTTPS:** É fundamental usar HTTPS tanto para o frontend quanto para o backend em ambiente de produção para garantir a segurança dos dados.
*   **CI/CD (Integração Contínua/Implantação Contínua):** Para implantações mais robustas, eficientes e automatizadas, configure um pipeline de CI/CD. Ferramentas como GitHub Actions, GitLab CI, ou Jenkins podem ser usadas para automatizar o processo de:
    1.  Rodar testes.
    2.  Gerar o build do frontend (`npm run build`).
    3.  Fazer o deploy dos arquivos estáticos para o ambiente de hospedagem escolhido (ex: copiar para o servidor Nginx, fazer upload para o S3).
    4.  (Opcional) Invalidar o cache do CDN (CloudFront) para o `index.html` e outros arquivos, se necessário.

## Recomendação para o MVP (se o backend já usa Nginx)

*   A **Estratégia A (Servir com Nginx)** é uma excelente opção inicial se você já possui Nginx configurado para o backend Django. Ela centraliza a infraestrutura e simplifica a configuração de CORS.
*   Se a escalabilidade e performance global forem preocupações imediatas, ou se você preferir um desacoplamento completo, a **Estratégia C (Serviço de Hospedagem de Sites Estáticos)** é uma alternativa robusta, embora com uma curva de aprendizado inicial um pouco maior para a configuração da nuvem.

Este documento serve como um guia para o processo de build e implantação do frontend. A execução real dependerá da infraestrutura específica e das ferramentas escolhidas para a hospedagem.
```
