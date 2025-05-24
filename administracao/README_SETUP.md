# Administração Module Setup Instructions

This document provides instructions for setting up the `administracao` Django app within the main Pizzeria SaaS project. This app provides API endpoints and models for system administration.

## 1. Add to INSTALLED_APPS

In your main project's `settings.py` file (e.g., `pizzeria_project/settings.py`), you need to add `administracao.apps.AdministracaoConfig` to the `INSTALLED_APPS` list.

Ensure that other related apps like `atendimento_interno` (for Mesas), `pagamentos` (for Vendas Report), `whatsapp_bot` (for Produtos Vendidos Report), and `django.contrib.contenttypes` are also correctly configured.

Example `INSTALLED_APPS` configuration:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',

    # Our custom apps
    'whatsapp_bot.apps.WhatsappBotConfig',
    'atendimento_interno.apps.AtendimentoInternoConfig',
    # 'products.apps.ProductsConfig', # If a dedicated products app exists
    'cozinha_api.apps.CozinhaApiConfig',
    'pagamentos.apps.PagamentosConfig',
    'administracao.apps.AdministracaoConfig', # New app for administration
    # ... other apps
]
```

## 2. Configure Database

Ensure your `settings.py` has the correct database configuration for PostgreSQL.

## 3. Configure Root URLconf

Include the URLs from `administracao.urls` in your main project's URL configuration file (e.g., `project_urls.py`). The URLs for this app are designed to be included under an `/api/admin/` prefix.

Example in `project_urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls), # Django Admin interface
    path('api/whatsapp/', include('whatsapp_bot.urls', namespace='whatsapp_bot')),
    path('api/', include('atendimento_interno.urls', namespace='atendimento_interno')),
    path('api/cozinha/', include('cozinha_api.urls', namespace='cozinha_api')),
    path('api/pagamentos/', include('pagamentos.urls', namespace='pagamentos')),
    path('api/admin/', include('administracao.urls', namespace='administracao')), # For Admin APIs
    # ... other app URLs
]
```

## 4. Model Definitions

*   **`ConfiguracaoSistema`**: Defined in `administracao/models.py`. Manages system-wide settings.
*   **`ProdutoPlaceholder`, `CategoriaProdutoPlaceholder`**: Also defined in `administracao/models.py`.
    *   **Important:** These are placeholder models. If a dedicated `products` app is created (or already exists) with `Produto` and `CategoriaProduto` models, these placeholders in `administracao.models` should be **removed or marked as unmanaged (`class Meta: managed = False`)**. The `administracao` app's serializers and views should then be updated to import and use the models from the `products` app directly.

## 5. Make Migrations and Migrate

After setting up the app:
*   If using the placeholder product/category models from `administracao.models` for the first time, run:
    ```bash
    python manage.py makemigrations administracao
    python manage.py migrate administracao
    ```
*   If a `products` app is introduced or already manages these tables, ensure its migrations are run, and `administracao` might not need new migrations for those specific models if they are marked as unmanaged or removed.
*   Always run `python manage.py migrate` to apply any pending migrations from other apps.

## 6. Django Admin Interface Setup

*   **`ConfiguracaoSistema`**: Registered in `administracao/admin.py`.
*   **`Produto` & `CategoriaProduto`**: If using the placeholder models, their admin registration is commented out in `administracao/admin.py`. If these models reside in a `products` app, ensure they are registered in `products/admin.py`.
*   **`Mesa`**: Ensure it's registered in `atendimento_interno/admin.py`.
*   **Usuários e Grupos**:
    1.  Access the Django Admin panel (usually at `/admin/`).
    2.  Go to "Authentication and Authorization" -> "Groups".
    3.  Create groups: "Administradores", "Atendentes", "Cozinheiros".
    4.  Go to "Users" and assign users to these groups as needed. Set appropriate permissions for users (e.g., staff status, superuser status for main admin).

## 7. API Endpoints for Administration

The following API endpoints are available under the `/api/admin/` prefix:

*   **Categorias de Produto (Placeholder):**
    *   `GET, POST /api/admin/categorias/`
    *   `GET, PUT, DELETE /api/admin/categorias/{id}/`
*   **Produtos (Placeholder):**
    *   `GET, POST /api/admin/produtos/`
    *   `GET, PUT, DELETE /api/admin/produtos/{id}/`
*   **Mesas (configuração):**
    *   `GET, POST /api/admin/mesas/`
    *   `GET, PUT, DELETE /api/admin/mesas/{id}/`
*   **Configurações do Sistema:**
    *   `GET, POST /api/admin/configuracoes/`
    *   `GET, PUT, DELETE /api/admin/configuracoes/{chave}/` (uses `chave` as the lookup)
*   **Relatórios:**
    *   `GET /api/admin/relatorios/vendas_simples/` (Params: `data_inicio`, `data_fim`)
    *   `GET /api/admin/relatorios/produtos_vendidos_simples/` (Params: `data_inicio`, `data_fim`)

Refer to `administracao/urls.py` and `administracao/views.py` for details. **Permissions for these admin APIs should be configured (e.g., using DRF's permission classes like `IsAdminUser`).**

## 8. Pré-população de Configurações

For `ConfiguracaoSistema`, consider creating a data migration to pre-populate essential keys after the initial schema migration, or add them manually via the Django Admin:
*   `NOME_PIZZARIA`: (Ex: "Pizzaria Delícia")
*   `TELEFONE_CONTATO`: (Ex: "+5511999998888")
*   `CHAVE_PIX_ESTATICA`: (Ex: "sua-chave-pix-aqui")
*   `HORARIO_FUNCIONAMENTO_INI`: (Ex: "18:00")
*   `HORARIO_FUNCIONAMENTO_FIM`: (Ex: "23:59")

This setup provides the backend foundation for the administration module as per the MVP.
```
