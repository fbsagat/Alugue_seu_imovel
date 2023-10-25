# 001: -----------------------------------------------
def loja_info(configs):
    """ Esta função deve retornar um dicionário com os cards da loja
    Cada item deve conter uma lista com as seguintes informações e na mesma ordem:
    Nome do card(nome), percentual de desconto para o card(desconto_porcent), quantidade de tickets(ticket_qtd),
     valor do pacote(btc e brl)(valor_pct_brl, valor_pct_btc), valor por ticket no pacote(btc e brl)
     (valor_por_ticket_brl, valor_por_ticket_btc) e desconto percentual por unidade(btc e brl)(desconto_p_un_brl,
     desconto_p_un_btc).
    """

    pacotes_nomes = ['Pacote Pequeno', 'Pacote Médio', 'Pacote Grande', 'Pacote Gigante']
    valor_ticket = configs.ticket_valor_base_brl
    pacote_qtd_inicial = configs.pacote_qtd_inicial
    pacote_qtd_mult = configs.pacote_qtd_multiplicador
    desconto_multiplicador = configs.desconto_pacote_multiplicador
    desconto_add_cripto = configs.desconto_add_bitcoin

    cards = []
    for n, pacote in enumerate(pacotes_nomes):
        ticket_qtd = pacote_qtd_inicial + (10 * n) + (n * pacote_qtd_mult)
        desconto_porcent = desconto_multiplicador * n

        valor_por_ticket_brl = valor_ticket - (valor_ticket * desconto_porcent / 100)
        valor_pacote_brl = valor_por_ticket_brl * ticket_qtd
        valor_por_ticket_btc = valor_ticket - (valor_ticket * (desconto_porcent+desconto_add_cripto) / 100)
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
