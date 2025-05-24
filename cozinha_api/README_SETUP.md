# Cozinha API Module Setup Instructions

This document provides instructions for setting up the `cozinha_api` Django app within the main Pizzeria SaaS project. This app provides API endpoints for the kitchen interface.

## 1. Add to INSTALLED_APPS

In your main project's `settings.py` file (e.g., `pizzeria_project/settings.py`), you need to add `cozinha_api.apps.CozinhaApiConfig` to the `INSTALLED_APPS` list.

Ensure that `whatsapp_bot` and `atendimento_interno` apps are also correctly configured if they haven't been already, as `cozinha_api` relies on their models.

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
    # 'products.apps.ProductsConfig', # Ensure the products app is also listed
    'cozinha_api.apps.CozinhaApiConfig', # New app for kitchen API
    # ... other apps
]
```

## 2. Configure Database

Ensure your `settings.py` has the correct database configuration for PostgreSQL. The changes made to `PedidoWhatsApp` and `PedidoMesa` models (addition of `status_cozinha` and `horario_entrada_cozinha`) will be applied to your database.

## 3. Configure Root URLconf

Include the URLs from `cozinha_api.urls` in your main project's URL configuration file (e.g., `project_urls.py` or `pizzeria_project/urls.py`). The URLs for this app are designed to be included under an `/api/cozinha/` prefix.

Example in `project_urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/whatsapp/', include('whatsapp_bot.urls', namespace='whatsapp_bot')),
    path('api/', include('atendimento_interno.urls', namespace='atendimento_interno')),
    path('api/cozinha/', include('cozinha_api.urls', namespace='cozinha_api')), # For Cozinha APIs
    # ... other app URLs
]
```
This will make the `cozinha_api` API endpoints available, for example:
*   `GET /api/cozinha/pedidos_para_preparar/`
*   `PATCH /api/cozinha/pedidos/{tipo_origem}/{id_pedido_origem}/status/`

## 4. Model Dependencies and Changes

The `cozinha_api` app itself does not define new Django models but relies on:
*   `whatsapp_bot.models.PedidoWhatsApp`
*   `atendimento_interno.models.PedidoMesa`

These models have been modified to include `status_cozinha` and `horario_entrada_cozinha` fields. Ensure these changes are correctly reflected in your database.

## 5. Make Migrations and Migrate

After setting up the app and ensuring all model changes in `whatsapp_bot` and `atendimento_interno` are saved, run migrations:

```bash
# First, ensure migrations for the apps with model changes are created
python manage.py makemigrations whatsapp_bot
python manage.py makemigrations atendimento_interno

# Then, migrate the database
python manage.py migrate
```
This will apply the new fields (`status_cozinha`, `horario_entrada_cozinha`) to the respective tables. The `cozinha_api` app itself doesn't require migrations as it has no models.

## 6. API Endpoints for Kitchen Frontend

The following API endpoints are now available for the kitchen frontend:

*   **`GET /api/cozinha/pedidos_para_preparar/`**:
    *   Lists all orders (from WhatsApp and Mesa) that are `AguardandoPreparo` or `EmPreparo`.
    *   Provides a consolidated view of items for each order.
*   **`PATCH /api/cozinha/pedidos/{tipo_origem}/{id_pedido_origem}/status/`**:
    *   Updates the `status_cozinha` for a specific order.
    *   `tipo_origem` can be `whatsapp` or `mesa`.
    *   `id_pedido_origem` is the ID of the `PedidoWhatsApp` or `PedidoMesa`.
    *   Payload example: `{ "status_cozinha": "EmPreparo" }` or `{ "status_cozinha": "Pronto" }`.

Refer to `cozinha_api/urls.py` and `cozinha_api/views.py` for details on these endpoints.

## 7. Business Logic Adjustments

*   **WhatsApp Orders:** When a user confirms payment by sending 'PAGO', the `PedidoWhatsApp` is now automatically updated with `status_cozinha = 'AguardandoPreparo'` and `horario_entrada_cozinha`.
*   **Table Orders:** When an item is added to an 'Aberto' `PedidoMesa` (and the order is not already in a kitchen processing state like 'EmPreparo' or 'Pronto'), the `PedidoMesa` is updated with `status_cozinha = 'AguardandoPreparo'` and `horario_entrada_cozinha`.

These adjustments ensure that confirmed orders are routed to the kitchen queue.
```
