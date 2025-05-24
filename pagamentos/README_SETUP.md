# Pagamentos Module Setup Instructions

This document provides instructions for setting up the `pagamentos` Django app within the main Pizzeria SaaS project. This app is responsible for managing payment records.

## 1. Add to INSTALLED_APPS

In your main project's `settings.py` file (e.g., `pizzeria_project/settings.py`), you need to add `pagamentos.apps.PagamentosConfig` to the `INSTALLED_APPS` list.

Ensure that other related apps like `whatsapp_bot`, `atendimento_interno`, and `django.contrib.contenttypes` (for GenericForeignKey) are also correctly configured.

Example `INSTALLED_APPS` configuration:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes', # Required for GenericForeignKey
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',

    # Our custom apps
    'whatsapp_bot.apps.WhatsappBotConfig',
    'atendimento_interno.apps.AtendimentoInternoConfig',
    # 'products.apps.ProductsConfig',
    'cozinha_api.apps.CozinhaApiConfig',
    'pagamentos.apps.PagamentosConfig', # New app for payments
    # ... other apps
]
```

## 2. Configure Database

Ensure your `settings.py` has the correct database configuration for PostgreSQL.

## 3. Configure Root URLconf

If you intend to use the API for listing payments (which is provided but noted as non-essential for MVP if Admin viewing is sufficient), include the URLs from `pagamentos.urls` in your main project's URL configuration file (e.g., `project_urls.py`).

Example in `project_urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/whatsapp/', include('whatsapp_bot.urls', namespace='whatsapp_bot')),
    path('api/', include('atendimento_interno.urls', namespace='atendimento_interno')),
    path('api/cozinha/', include('cozinha_api.urls', namespace='cozinha_api')),
    path('api/pagamentos/', include('pagamentos.urls', namespace='pagamentos')), # For Pagamentos APIs
    # ... other app URLs
]
```
This will make the `pagamentos` API endpoints available, for example:
*   `GET /api/pagamentos/pedido/{tipo_origem}/{id_pedido_origem}/`

## 4. Model Definition (`Pagamento`)

The `Pagamento` model is defined in `pagamentos/models.py` and uses a `GenericForeignKey` (`content_type`, `object_id`, `pedido`) to link to either `PedidoWhatsApp` or `PedidoMesa`. It includes fields for `metodo_pagamento`, `valor_pago`, `status_pagamento`, etc.

## 5. Service Function (`registrar_pagamento_para_pedido`)

A service function is available in `pagamentos/services.py` to create `Pagamento` records. This service is used by:
*   `whatsapp_bot.views.py`: When a PIX payment is manually confirmed for a `PedidoWhatsApp`.
*   `atendimento_interno.views.py`: When a payment is registered for a `PedidoMesa`.

## 6. Make Migrations and Migrate

After setting up the app, run migrations:

```bash
python manage.py makemigrations pagamentos
python manage.py migrate
```
This will create the `pagamentos_pagamento` table in your database.

## 7. Admin Panel

The `Pagamento` model is registered in `pagamentos/admin.py`, allowing for viewing and manual management of payment records via the Django Admin interface. This is the primary way to view payments in the MVP.

## 8. API Endpoint for Listing Payments (Optional for MVP usage)

*   **`GET /api/pagamentos/pedido/{tipo_origem}/{id_pedido_origem}/`**:
    *   Lists all payment records associated with a specific order.
    *   `tipo_origem` can be `whatsapp` or `mesa`.
    *   `id_pedido_origem` is the ID of the `PedidoWhatsApp` or `PedidoMesa`.

This endpoint is available for querying payment history if needed, complementing the Admin view.

## MVP Payment Flows:

*   **WhatsApp Orders (PIX Manual):**
    1.  Customer is informed of a static PIX key.
    2.  Customer sends 'PAGO' or a comprovante.
    3.  Bot acknowledges and updates `PedidoWhatsApp` to `status_cozinha = 'AguardandoPreparo'`.
    4.  A `Pagamento` record is created with `metodo_pagamento='pix'`, `status_pagamento='Aprovado'`.
    5.  An attendant manually verifies the PIX payment by checking bank statements and then proceeds with the order in the backend/kitchen system (details of this manual verification are outside the bot's direct actions).
*   **Table Orders (Manual Registration):**
    1.  Attendant uses the `POST /api/pedidos_mesa/{pedido_id}/registrar_pagamento/` endpoint.
    2.  A `Pagamento` record is created with the provided details (method, amount) and `status_pagamento='Aprovado'`.
    3.  The `PedidoMesa` status is updated to 'Pago', and the `Mesa` status to 'Livre'.

This setup fulfills the backend requirements for the MVP of the Pagamentos module.
```
