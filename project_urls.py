from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include the URLs from the whatsapp_bot app
    path('whatsapp/', include('whatsapp_bot.urls', namespace='whatsapp_bot')),
    # Other app URLs would be included here as well
    # path('products/', include('products.urls', namespace='products')),
    # path('orders/', include('orders.urls', namespace='orders')),
]

# Instructions for settings.py (typically in a project_name/settings.py file):
# 1. Ensure 'whatsapp_bot.apps.WhatsappBotConfig' is in INSTALLED_APPS.
# 2. Ensure 'products.apps.ProductsConfig' (once created) is in INSTALLED_APPS.
# 3. Configure database settings (PostgreSQL).
# 4. Configure ROOT_URLCONF = 'project_urls' (or the appropriate path to this file).
# 5. Set up Twilio API keys and other necessary settings.
# 6. Configure logging.
#
# Example for INSTALLED_APPS:
# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     'whatsapp_bot.apps.WhatsappBotConfig',
#     # 'products.apps.ProductsConfig', # Add when product app is created
#     # ... other apps
# ]
