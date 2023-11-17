from django.contrib import admin
from .models import PacoteConfig, PagamentoInvoice


@admin.register(PacoteConfig)
class PacoteConfigAdmin(admin.ModelAdmin):
    list_display = (
        'ticket_valor_base_brl', 'pacote_qtd_inicial', 'pacote_qtd_multiplicador', 'desconto_pacote_multiplicador',
        'desconto_add_bitcoin', 'data_registro')
    non_editable_fields = ['data_registro']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['ticket_valor_base_brl', 'pacote_qtd_inicial', 'pacote_qtd_multiplicador',
                    'desconto_pacote_multiplicador', 'desconto_add_bitcoin', 'data_registro']
        else:
            return []


@admin.register(PagamentoInvoice)
class PagamentoInvoiceAdmin(admin.ModelAdmin):
    list_display = ('do_usuario', 'do_config', 'do_pacote', 'pago', 'btc', 'checkout_id', 'data_registro')
    readonly_fields = ('data_registro',)
