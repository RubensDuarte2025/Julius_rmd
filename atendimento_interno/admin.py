from django.contrib import admin
# from .models import Mesa, PedidoMesa, ItemPedidoMesa

# Register your models here.
# admin.site.register(Mesa)
# admin.site.register(PedidoMesa)
# admin.site.register(ItemPedidoMesa)

# Basic customization example (optional for MVP)
# class MesaAdmin(admin.ModelAdmin):
#     list_display = ('numero_identificador', 'status', 'capacidade_default')
#     list_filter = ('status',)
#     search_fields = ('numero_identificador',)

# class ItemPedidoMesaInline(admin.TabularInline):
#     model = ItemPedidoMesa
#     extra = 1 # Number of empty forms to display

# class PedidoMesaAdmin(admin.ModelAdmin):
#     list_display = ('id', 'mesa', 'status_pedido', 'data_abertura', 'total_pedido') # Assuming a total_pedido method
#     list_filter = ('status_pedido', 'data_abertura')
#     search_fields = ('mesa__numero_identificador', 'id')
#     inlines = [ItemPedidoMesaInline]

#     def total_pedido(self, obj):
#         # This would ideally be a method or property on the PedidoMesa model
#         return obj.calcular_total() # Placeholder, assuming PedidoMesa has this method
#     total_pedido.short_description = 'Total do Pedido'

# admin.site.register(Mesa, MesaAdmin)
# admin.site.register(PedidoMesa, PedidoMesaAdmin)
