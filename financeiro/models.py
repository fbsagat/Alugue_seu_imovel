from django.db import models


pacotes_nomes = ['Pacote Pequeno', 'Pacote Médio', 'Pacote Grande', 'Pacote Gigante']


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

    def loja_info(self):
        """ Esta função deve retornar um dicionário com os cards da loja
        Cada item deve conter uma lista com as seguintes informações e na mesma ordem:
        Nome do card(nome), percentual de desconto para o card(desconto_porcent), quantidade de tickets(ticket_qtd),
         valor do pacote(btc e brl)(valor_pct_brl, valor_pct_btc), valor por ticket no pacote(btc e brl)
         (valor_por_ticket_brl, valor_por_ticket_btc) e desconto percentual por unidade(btc e brl)(desconto_p_un_brl,
         desconto_p_un_btc).
        """

        valor_ticket = self.ticket_valor_base_brl
        pacote_qtd_inicial = self.pacote_qtd_inicial
        pacote_qtd_mult = self.pacote_qtd_multiplicador
        desconto_multiplicador = self.desconto_pacote_multiplicador
        desconto_add_cripto = self.desconto_add_bitcoin

        cards = []
        for n, pacote in enumerate(pacotes_nomes):
            ticket_qtd = pacote_qtd_inicial + (10 * n) + (n * pacote_qtd_mult)
            desconto_porcent = desconto_multiplicador * n
            valor_por_ticket_brl = valor_ticket - (valor_ticket * desconto_porcent / 100)
            valor_pacote_brl = valor_por_ticket_brl * ticket_qtd
            valor_por_ticket_btc = valor_ticket - (valor_ticket * (desconto_porcent + desconto_add_cripto) / 100)
            valor_pacote_btc = valor_por_ticket_btc * ticket_qtd
            desconto_p_un_btc = desconto_porcent + desconto_add_cripto

            pacote = {
                'nome': pacote,
                'ticket_qtd': ticket_qtd,
                'desconto_porcent': desconto_porcent,
                'valor_pct_brl': f'{valor_pacote_brl:.2f}',
                'valor_pct_btc': f'{round(valor_pacote_btc, 2):.2f}',
                'valor_por_ticket_brl': f'{round(valor_por_ticket_brl, 2):.2f}',
                'valor_por_ticket_btc': f'{round(valor_por_ticket_btc, 2):.2f}',
                'desconto_p_un_brl': desconto_porcent,
                'desconto_p_un_btc': desconto_p_un_btc,
            }
            cards.append(pacote)
        return cards


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