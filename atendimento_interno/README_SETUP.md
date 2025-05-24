# Atendimento Interno (Mesas) Module Setup Instructions

This document provides instructions for setting up the `atendimento_interno` Django app within the main Pizzeria SaaS project.

## 1. Add to INSTALLED_APPS

In your main project's `settings.py` file (e.g., `pizzeria_project/settings.py`), you need to add `atendimento_interno.apps.AtendimentoInternoConfig` to the `INSTALLED_APPS` list.

You will also need Django REST Framework if it's not already included.

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
    'whatsapp_bot.apps.WhatsappBotConfig', # If using the WhatsApp bot
    'atendimento_interno.apps.AtendimentoInternoConfig',
    # 'products.apps.ProductsConfig', # Ensure the products app is also listed
    # ... other apps for payments, kitchen, etc.
]
```

## 2. Configure Database

Ensure your `settings.py` has the correct database configuration for PostgreSQL, as defined in the system architecture.

## 3. Configure Root URLconf

Include the URLs from `atendimento_interno.urls` in your main project's URL configuration file (e.g., `project_urls.py` or `pizzeria_project/urls.py`). The URLs for this app are designed to be included under an `/api/` prefix.

Example in `project_urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/whatsapp/', include('whatsapp_bot.urls', namespace='whatsapp_bot')), # Example for whatsapp_bot
    path('api/', include('atendimento_interno.urls', namespace='atendimento_interno')), # For atendimento_interno APIs
    # ... other app URLs
]
```
This will make the `atendimento_interno` API endpoints available under `/api/mesas/`, `/api/pedidos_mesa/`, etc.

## 4. Product Model Dependency

The `atendimento_interno` app currently uses a placeholder `Produto` model in its `models.py` and `serializers.py`. For full functionality, this placeholder needs to be replaced with the actual `Produto` model from your `products` app (or equivalent app managing product data).

**Actions Required:**
*   In `atendimento_interno/models.py`:
    *   Remove or comment out the placeholder `Produto` class.
    *   Change `from .models import Produto` (if it was importing the placeholder) to `from products.models import Produto` (adjust `products` to your actual app name).
    *   Ensure `ForeignKey` relationships to `Produto` point to the correct model string (e.g., `'products.Produto'`) if using string references, or the imported class.
*   In `atendimento_interno/serializers.py`:
    *   Remove or comment out the placeholder `ProdutoSerializer`.
    *   Change imports to use `Produto` and `ProdutoSerializer` from the `products` app.
    *   Ensure `PrimaryKeyRelatedField` for `produto_id` correctly queries `Produto.objects.all()` from the actual `products` app.

## 5. Make Migrations and Migrate

After setting up the app, integrating the actual `Produto` model, and ensuring all dependencies are met, run migrations:

```bash
python manage.py makemigrations atendimento_interno
# May also need to run for 'products' if it's new or changed
python manage.py migrate
```

This will create the necessary tables in your PostgreSQL database: `atendimento_interno_mesa`, `atendimento_interno_pedidomesa`, and `atendimento_interno_itempedidomesa`.

## 6. API Endpoints

Once set up and migrated, the following API endpoints (among others defined in `urls.py`) will be available:

*   **Mesas:**
    *   `GET /api/mesas/`
    *   `GET /api/mesas/{mesa_id}/`
    *   `PATCH /api/mesas/{mesa_id}/atualizar-status/`
    *   `POST /api/mesas/{mesa_id}/pedidos/` (Criar pedido para mesa)
*   **Pedidos de Mesa:**
    *   `GET /api/pedidos_mesa/{pedido_id}/`
    *   `PATCH /api/pedidos_mesa/{pedido_id}/`
    *   `POST /api/pedidos_mesa/{pedido_id}/registrar-pagamento/`
*   **Itens do Pedido de Mesa:**
    *   `GET, POST /api/pedidos_mesa/{pedido_mesa_pk}/itens/`
    *   `GET, PUT, PATCH, DELETE /api/pedidos_mesa/{pedido_mesa_pk}/itens/{item_pk}/`

Refer to `atendimento_interno/urls.py` and `atendimento_interno/views.py` for the complete list of available actions and their corresponding URLs.

## 7. Frontend Development

The React frontend will consume these APIs. Ensure the frontend developers are aware of these endpoints and the expected request/response payloads.
The placeholder `Produto` model currently has `id`, `nome`, and `preco_base`. The actual `Produto` model might have more fields, which should be reflected in the `ProdutoSerializer` used by this app.
```
