from django.db import models

# Este app não define seus próprios modelos Django, pois opera
# sobre modelos existentes de outros apps (whatsapp_bot, atendimento_interno).
# Ele é usado para centralizar a lógica da API da Cozinha.

# Se houvesse necessidade de modelos específicos para a cozinha no futuro
# (ex: preferências de visualização do cozinheiro, logs específicos da cozinha),
# eles seriam definidos aqui. Para o MVP atual, não são necessários.
