from django.db import models


class PacoteConfig(models.Model):
    ticket_valor_base_brl = models.FloatField(null=False, help_text='Apenas números pares')
    pacote_qtd_inicial = models.IntegerField(null=False)
    pacote_qtd_multiplicador = models.IntegerField(null=False)
    desconto_pacote_multiplicador = models.IntegerField(null=False, help_text='Percentual')
    desconto_add_bitcoin = models.IntegerField(null=False, help_text='Percentual')
    data_registro = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Pacotes configs'

    def __str__(self):
        return f'Configs de: {self.data_registro} / Valor base: R${self.ticket_valor_base_brl}'


class PagamentoInvoice(models.Model):
    do_usuario = models.ForeignKey('home.Usuario', null=False, blank=False, on_delete=models.DO_NOTHING)
    do_pacote = models.ForeignKey('PacoteConfig', null=False, blank=False, on_delete=models.DO_NOTHING)
    btc = models.BooleanField(default=False, help_text='Marque se o pagamento foi em bitcoin')
    pago = models.BooleanField(default=False)
    dados = models.JSONField(null=True, blank=True)
    data_registro = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Invoices'

    def __str__(self):
        return f'{self.do_usuario} - {self.do_pacote} - {self.data_registro}{" - PG" if self.pago else ""}'