# WhatsApp Bot Setup Instructions

This document provides instructions for setting up the `whatsapp_bot` Django app within the main Pizzeria SaaS project.

## 1. Add to INSTALLED_APPS

In your main project's `settings.py` file (e.g., `pizzeria_project/settings.py` or a similar path), you need to add `whatsapp_bot.apps.WhatsappBotConfig` to the `INSTALLED_APPS` list.

If you also have a `products` app (for `Produtos` and `CategoriasProdutos` models), ensure it's also added.

Example `INSTALLED_APPS` configuration:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Our custom apps
    'whatsapp_bot.apps.WhatsappBotConfig',
    # 'products.apps.ProductsConfig', # Uncomment or add when the products app is created
    # ... other apps for payments, kitchen, etc.

    # Third-party apps if any (e.g., 'rest_framework' if using DRF)
]
```

## 2. Configure Database

Ensure your `settings.py` has the correct database configuration to use PostgreSQL, as defined in the system architecture. The `whatsapp_bot` app (and others) will use this database.

Example `DATABASES` configuration:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pizzeria_db_name',    # Replace with your DB name
        'USER': 'pizzeria_db_user',    # Replace with your DB user
        'PASSWORD': 'pizzeria_db_password', # Replace with your DB password
        'HOST': 'localhost',        # Or your DB host (e.g., an AWS RDS endpoint)
        'PORT': '5432',             # Default PostgreSQL port
    }
}
```

## 3. Configure Root URLconf

If you are using the `project_urls.py` file created at the root of the repository (or a similarly named main URL configuration file), ensure your `settings.py` points to it.

Example `ROOT_URLCONF` configuration:

```python
# In settings.py
ROOT_URLCONF = 'project_urls' # If project_urls.py is in the Python path (e.g., root)
# Or, if project_urls.py is inside a project directory like 'pizzeria_project':
# ROOT_URLCONF = 'pizzeria_project.urls'
```

## 4. Twilio (or other BSP) Credentials

You will need to store your Twilio Account SID, Auth Token, and Twilio WhatsApp phone number securely. It's recommended to use environment variables or Django settings for this, rather than hardcoding them.

Example (in `settings.py`):

```python
# In settings.py
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER') # e.g., 'whatsapp:+14155238886'
```
Remember to set these environment variables in your deployment environment.

## 5. Logging Configuration (Recommended)

Configure Django's logging to capture information, warnings, and errors, especially for the webhook interactions.

Example basic logging (in `settings.py`):

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO', # Adjust level as needed (DEBUG, INFO, WARNING, ERROR)
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'whatsapp_bot': { # Specific logger for your app
            'handlers': ['console'],
            'level': 'DEBUG', # More verbose for app development
            'propagate': False,
        },
    }
}
```

## 6. Make Migrations and Migrate

After setting up the app and database, you'll need to create and apply database migrations:

```bash
python manage.py makemigrations whatsapp_bot
# python manage.py makemigrations products # (if products app is new)
python manage.py migrate
```

This will create the necessary tables in your PostgreSQL database, including `whatsapp_bot_pedidowhatsapp`.

## 7. Running the Development Server

Once configured, you can run the Django development server:

```bash
python manage.py runserver
```
Your webhook endpoint (e.g., `http://localhost:8000/whatsapp/webhook/` or `http://your_public_ngrok_url/whatsapp/webhook/` if using ngrok for Twilio testing) should then be configurable in the Twilio console.

## 8. Next Steps for `whatsapp_bot` development

*   Implement the full conversation logic in `whatsapp_bot/views.py` as per the subtask requirements.
*   Integrate with `products` app models for fetching categories and products.
*   Write unit and integration tests.
```
