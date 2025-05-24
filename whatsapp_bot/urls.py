from django.urls import path
from . import views

app_name = 'whatsapp_bot'

urlpatterns = [
    path('webhook/', views.whatsapp_webhook, name='whatsapp_webhook'),
    # Adicionar outras URLs específicas do bot aqui se necessário no futuro
]
