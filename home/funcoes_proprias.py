def valor_br(valor):
    """ O valor deve ser inteiro e vir em format string e será convertido para valor financeiro em Reais(R$) onde as
    duas últimas casas sempre representarão centavos Ex: de 134567899 para 1.345.678,99"""
    virgola = str(',') if int(valor) > 99 else str('0,')
    y = '' if int(valor) < 100 else f'{int(valor[:-2]):_.2f}'.replace('_', '.')
    z = f'{y[:-3]}{virgola}{str(valor)[-2:]}'
    return f'R${z}'
