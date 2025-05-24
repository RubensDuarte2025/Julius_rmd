from django.contrib import admin
from .models import Pagamento

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'content_type', 'object_id', 'pedido_object', 'metodo_pagamento', 
        'valor_pago', 'status_pagamento', 'data_hora_pagamento'
    )
    list_filter = ('metodo_pagamento', 'status_pagamento', 'data_hora_pagamento', 'content_type')
    search_fields = ('id', 'object_id') # Search by the ID of the related order
    readonly_fields = ('data_hora_pagamento', 'content_type', 'object_id', 'pedido_object') # Make GFK fields read-only in admin

    def pedido_object(self, obj):
        # Display a link to the related order in admin, if possible
        if obj.pedido:
            return str(obj.pedido)
        return None
    pedido_object.short_description = 'Pedido Associado'

# Note: For GenericForeignKey, direct search/filter on the related object's fields
# in list_filter or search_fields is more complex and might require custom admin logic
# or third-party packages if deep inspection is needed.
# The current setup allows filtering by the type of order (content_type).
