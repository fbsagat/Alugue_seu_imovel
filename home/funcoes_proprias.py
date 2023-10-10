import io, os
from math import ceil
from textwrap import wrap

from django.core.exceptions import ValidationError
from num2words import num2words

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.colors import HexColor
from xhtml2pdf import pisa

from Alugue_seu_imovel import settings


# 001: -----------------------------------------------
def valor_format(valor):
    """ O valor deve ser inteiro e vir em format string e será convertido para valor financeiro em Reais(R$) onde as
    duas últimas casas sempre representarão centavos Ex: de 134567899 para 1.345.678,99"""
    virgola = str(',') if int(valor) > 99 else str('0,')
    y = '' if int(valor) < 100 else f'{int(valor[:-2]):_.2f}'.replace('_', '.')
    z = f'{y[:-3]}{virgola}{str(valor)[-2:]}'
    return f'R${z}'


# 002: -----------------------------------------------
def cpf_format(cpf):
    if cpf is None:
        return None
    else:
        return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}'


# 003: -----------------------------------------------
def cel_format(cel):
    return f'({cel[:2]}) {cel[2:7]}-{cel[7:11]}'


# 004: -----------------------------------------------
def cep_format(cep):
    return f'{cep[:5]}-{cep[5:8]}'


# 005: -----------------------------------------------
def tratar_imagem(arquivo_obj):
    size = arquivo_obj.file.size
    limite_mb = settings.TAMANHO_DAS_IMAGENS_Mb
    if size > limite_mb * 1024 * 1024:
        raise ValidationError(f"O arquivo não deve ser maior que {str(limite_mb)}Mb")


# 006: -----------------------------------------------

def valor_por_extenso(valor):
    if type(valor) == str:
        reais = valor[:-2]
        centavos = valor[-2:]
        centavos_format = f' e {num2words(int(centavos), lang="pt_BR")} centavos'
        return f'{num2words(int(reais), lang="pt_BR").capitalize()} reais{centavos_format if int(centavos) > 1 else ""}'
    else:
        return None


# 007: -----------------------------------------------


def validar_cpf(cpf):
    # Remove todos os caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, cpf))

    # Verifica se o CPF tem 11 dígitos
    if len(cpf) != 11:
        return False

    # Calcula o primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = soma % 11
    if resto < 2:
        digito1 = 0
    else:
        digito1 = 11 - resto

    # Calcula o segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = soma % 11
    if resto < 2:
        digito2 = 0
    else:
        digito2 = 11 - resto

    # Verifica se os dígitos verificadores estão corretos
    if int(cpf[9]) == digito1 and int(cpf[10]) == digito2:
        return True
    else:
        return False


# 008: -----------------------------------------------
def loja_info():
    """ Esta função deve retornar um dicionário com os cards da loja
    Cada item deve se chamar pelo título do card e deve conter uma lista com as seguintes informações e na mesma ordem:
    Quantidades de tickets(ambos), valor do pacote(btc e brl), valor por ticket no pacote(btc e brl),
    desconto percentual por unidade(btc e brl).
    """

    pacotes_nomes = ['Pacote Pequeno', 'Pacote Médio', 'Pacote Grande', 'Pacote Gigante']
    valor_ticket = settings.TICKET_VALOR_BASE_BRL
    pacote_qtd_inicial = settings.PACOTE_QTD_INICIAL
    pacote_qtd_mult = settings.PACOTE_QTD_MULTIPLICADOR
    desconto_multiplicador = settings.DESCONTO_PACOTE_MULTIPLICADOR
    desconto_add_cripto = settings.DESCONTO_ADD_BITCOIN

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


# 100: -----------------------------------------------
def gerar_um_recibo(pdf, pag_lar, pag_centro, recibo_n, pos_y, dados, parcelas):
    """ Ex:
        infos = {'cod_recibo': ['465736', '463416', '125736', '465676', '465756', '465346', '474936'],
             'cod_contrato': '4536-3382', 'nome_locador': 'FÁBIO AUGUSTO MACEDO DOS SANTOS', 'rg_locd': '5667789',
             'cpf_locd': '005.234.342-10', 'nome_locatario': 'SANDRA DINORIA CRAVO COUTINHO', 'rg_loct': '8798122',
             'cpf_loct': '235.632.142-04', 'valor_e_extenso': 'R$800,00 (OITOCENTOS REAIS)',
             'mes_e_ano': ['NOVEMBRO', '2022', 'DEZEMBRO', '2022', 'JANEIRO', '2023', 'FEVEREIRO', '2023', 'MARÇO', '2023',
                           'ABRIL', '2023', 'MAIO', '2023'],
             'endereco': "Passagem Péricles Guedes, 391, Apto 102 Castanheira Belém/PA 66645_290", 'cidade': 'Belém',
             'data': '________________, ____ de _________ de ________'}
    """

    rect_lar = pag_lar - (pag_lar * 10 / 100)
    rect_alt = pag_lar / 2.5

    rect_pos_x = pag_centro[0] - (rect_lar / 2)
    rect_pos_y = pos_y - (rect_alt / 2)

    pdf.rect(rect_pos_x, rect_pos_y, rect_lar, rect_alt)

    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawString(rect_pos_x + 5, rect_pos_y + rect_alt - 15, 'RECIBO DE PAGAMENTO DE ALUGUEL')

    pdf.setFont('Helvetica-Bold', 8)
    pdf.drawString(rect_pos_x + rect_lar - 213, rect_pos_y + rect_alt - 10,
                   f'Cód. recibo: {dados["cod_recibo"][recibo_n - 1]} / Cód. contrato: {dados["cod_contrato"]}')

    pdf.drawString(rect_pos_x + 12, rect_pos_y + 3,
                   f'Cód. recibo: {dados["cod_recibo"][recibo_n - 1]} / Cód. contrato: '
                   f'{dados["cod_contrato"]}')

    pdf.setFont('Helvetica-Bold', 10)

    texto_estilo = ParagraphStyle('My Para style', fontName='Times-Roman', fontSize=12, borderPadding=(20, 20, 20),
                                  leading=14, alignment=1)

    texto = Paragraph(
        f'Eu, <b>{dados["nome_locador"]}</b>, inscrito(a) no {dados["rg_locd"]} CPF sob o nº '
        f'{cpf_format(dados["cpf_locd"])}, recebi de <b>{dados["nome_locatario"]}</b>,'
        f' inscrito(a) no {dados["rg_loct"]} CPF sob o n° {cpf_format(dados["cpf_loct"])},'
        f' a importância de <b>{dados["valor_e_extenso"]}</b>, referente ao pagamento do aluguel'
        f' do mês de <b>{dados["mes_e_ano"][2 * (recibo_n - 1)]} DE '
        f'{dados["mes_e_ano"][(2 * (recibo_n - 1)) + 1]}</b> (Parcela {recibo_n} de um total '
        f'de {parcelas}), de um imóvel localizado no endereço: {dados["endereco"]}, declarando '
        f'portanto, plena, total e irrevogável quitação do mês referido a partir de então.'
        f' <BR/><BR/><i> Para maior clareza firmo o presente em:'
        f'<BR/>{dados["data_preenchimento"][recibo_n - 1]}</i><BR/><BR/><BR/>'
        f'___________________________________________________________________________________'
        f'<BR/>{dados["nome_locador"]}',
        texto_estilo)
    texto.wrapOn(pdf, 525, 110)
    texto.drawOn(pdf, rect_pos_x + 5, rect_pos_y + 15)


def gerar_uma_pagina_recibo(pdf, parcelas, pag_centro, pag_alt, pag_lar, pag_n, dados):
    recibos_qtd = pag_n * 3
    if recibos_qtd < parcelas + 1:
        gerar_um_recibo(pdf=pdf, pag_centro=pag_centro, pag_lar=pag_lar, recibo_n=recibos_qtd,
                        pos_y=pag_centro[1] - pag_alt * 33 / 100, dados=dados, parcelas=parcelas)
    if recibos_qtd < parcelas + 2:
        gerar_um_recibo(pdf=pdf, pag_centro=pag_centro, pag_lar=pag_lar, recibo_n=recibos_qtd - 1, pos_y=pag_centro[1],
                        dados=dados, parcelas=parcelas)
    if recibos_qtd < parcelas + 3:
        gerar_um_recibo(pdf=pdf, pag_centro=pag_centro, pag_lar=pag_lar, recibo_n=recibos_qtd - 2,
                        pos_y=pag_centro[1] + pag_alt * 33 / 100, dados=dados, parcelas=parcelas)


# Principal:
def gerar_recibos_pdf(dados):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setAuthor(f'{dados["nome_locador"]}')
    pdf.setTitle(f'Recibos do contrato {dados["cod_contrato"]}')
    pdf.setCreator(settings.SITE_URL)
    pdf.setSubject(f'Locatário: {dados["nome_locatario"]}')

    pag_lar = A4[0]
    pag_alt = A4[1]
    pag_centro = (pag_lar / 2, pag_alt / 2)

    parcelas = int(len(dados['mes_e_ano']) / 2)
    paginas = int((len(dados['mes_e_ano']) / 2) / 3) if (len(dados['mes_e_ano']) / 2) / 3 % 2 == 1 else ceil(
        (len(dados['mes_e_ano']) / 2) / 3)

    # Tratando itens opcionais \/
    dados['rg_locd'] = '' if dados['rg_locd'] == 'None' else f' RG sob o nº {dados["rg_locd"]} e '
    dados['rg_loct'] = f' RG sob o nº {dados["rg_loct"]} e ' if dados['rg_loct'] != '' else ''
    if dados['data_preenchimento']:
        pass
    else:
        for x in range(0, (len(dados['mes_e_ano']))):
            dados['data_preenchimento'].append(f"{dados['cidade']} ,____________, ____ de ____________ de ________")

    for pagina in range(paginas):
        page_num = pdf.getPageNumber()
        gerar_uma_pagina_recibo(pag_n=page_num, pag_alt=pag_alt, pag_centro=pag_centro, pag_lar=pag_lar,
                                parcelas=parcelas, dados=dados, pdf=pdf)
        pdf.showPage()

    pdf.save()
    buffer.seek(0)
    return buffer


# 101: -----------------------------------------------
def criar_uma_pagina_tabela(fazer, pag_n, a4h, dados, pdf, celula_altura):
    # Atributos da página
    pag_lar = a4h[0]
    pag_alt = a4h[1]
    pag_centro_h = pag_lar / 2
    pag_centro_v = pag_alt / 2

    # Customize a tabela
    celula_quantidade_h = len(dados['datas']) + 1
    celula_quantidade_v = fazer
    margem_vertical = 40
    margem_horizontal = 0
    celula_altura_max = 92

    if pag_n == 1:
        tam_calc = round((pag_alt / celula_quantidade_v) - (margem_vertical / celula_quantidade_v)) - 1
        celula_altura = tam_calc if tam_calc <= celula_altura_max else celula_altura_max
    celula_largura = round(pag_lar / celula_quantidade_h) - 1
    media_alt_larg = round(((celula_altura + celula_largura) / 2))

    # print('celula_altura: ', celula_altura, 'celula_largura: ', celula_largura, 'media: ', media_alt_larg)

    # Encaixe de texto
    text_wrap_imo = espacamento_h = espac_h_sinal = espacamento_v = text_tam_imo = text_wrap_parc = text_tam_parc = \
        leading = char_space = 0

    # Verticalmente (leading)
    if celula_altura <= 61:  # Célula pequena
        leading = 9
        espacamento_v = 12
        max_linhas = 4
    elif celula_altura <= 76:  # Célula média
        leading = 8.5
        espacamento_v = 12
        max_linhas = 5
    elif celula_altura <= 92:  # Célula grande
        leading = 12
        espacamento_v = 13
        max_linhas = 6

    # Horizontalmente  (wrap)
    if celula_largura <= 104:  # Célula pequena
        text_wrap_imo = 18
        text_wrap_parc = 30
        espacamento_h = 2
        espac_h_sinal = 9
        char_space = 0
    elif celula_largura <= 135:  # Célula média
        text_wrap_imo = 19
        text_wrap_parc = 32
        espacamento_h = 2
        espac_h_sinal = 9
        char_space = 0.1
    elif celula_largura <= 167:  # Célula grande
        text_wrap_imo = 19
        text_wrap_parc = 33
        espacamento_h = 3
        espac_h_sinal = 12
        char_space = 0.2

    # media (tam)
    if media_alt_larg <= 82:  # Célula pequena
        text_tam_imo = 11
        text_tam_parc = 8
    elif media_alt_larg <= 106:  # Célula média
        text_tam_imo = 11
        text_tam_parc = 8
    elif media_alt_larg <= 130:  # Célula grande
        text_tam_imo = 12
        text_tam_parc = 11

    # Calculos para organização
    tam_tt_h = celula_largura * celula_quantidade_h
    tam_tt_v = celula_altura * celula_quantidade_v
    centro_h = tam_tt_h / 2
    centro_v = tam_tt_v / 2
    inicia_em_h = (tam_tt_h / pag_lar) + (pag_centro_h - centro_h) - 1
    # \/ Para centralizar verticalmente: (tam_tt_v / pag_alt) + (pag_centro_v - centro_v)
    inicia_em_v = margem_vertical

    # Cria na horizontal
    for horizontal, y in enumerate(range(0, tam_tt_h, celula_largura)):
        # Cria na vertical
        for vertical, x in enumerate(range(0, tam_tt_v, celula_altura)):
            if vertical % 2 == 0:
                pdf.setFillColorRGB(0, 0, 0, 0.05)
            else:
                pdf.setFillColorRGB(0, 0, 0, 0)

            # Criar tabela
            pdf.rect(inicia_em_h + y, pag_alt - inicia_em_v - celula_altura - x, celula_largura, celula_altura, fill=1)
            pdf.rect(inicia_em_h + y, pag_alt - inicia_em_v - celula_altura - x, celula_largura, celula_altura, fill=1)
            pdf.setFillColorRGB(0, 0, 0, 1)

            # Criar textos
            if vertical == 0 and horizontal == 0:
                pdf.saveState()
                pdf.setLineWidth(0.01)
                pdf.setStrokeColor(colors.gray)
                pdf.rect(inicia_em_h + y, pag_alt - inicia_em_v - celula_altura - x + celula_altura + 20,
                         tam_tt_h, 15, stroke=1)
                pdf.restoreState()

                textobject = pdf.beginText(inicia_em_h + y + 2,
                                           pag_alt - inicia_em_v - celula_altura - x + celula_altura + 24)
                textobject.setFillColor(colors.dimgray)
                textobject.setFont('Helvetica-Bold', 11)
                textobject.textLine(
                    f'Tabela de agenda dos imóveis de '
                    f'{dados["usuario_username"]} (De {dados["datas"][0]} Até {dados["datas"][-1]})')
                pdf.drawText(textobject)

                textobject = pdf.beginText(inicia_em_h + y,
                                           pag_alt - inicia_em_v - celula_altura - x + celula_altura + 2)
                textobject.setFillColor(colors.black)
                textobject.setFont('Times-Roman', 14)
                textobject.textLine('Imóveis Ativos')
                pdf.drawText(textobject)

            if vertical == 0 and horizontal > 0:
                textobject = pdf.beginText(inicia_em_h + y,
                                           pag_alt - inicia_em_v - celula_altura - x + celula_altura + 2)
                textobject.setFillColor(colors.black)
                textobject.setFont('Times-Roman', 14)
                textobject.textLine(f'{dados["datas"][horizontal - 1]}')
                pdf.drawText(textobject)

            if vertical >= 0 and horizontal == 0:
                mytext = f'{dados["imoveis"]["nomes"][((pag_n - 1) * dados["imov_qtd"]) + vertical]}'
                wraped_text = "\n".join(wrap(mytext, text_wrap_imo))
                textobject = pdf.beginText(inicia_em_h + y + espacamento_h,
                                           pag_alt - inicia_em_v - x - espacamento_v)
                textobject.setFillColor(colors.black)
                textobject.setFont('Times-Roman', text_tam_imo)
                for n, line in enumerate(wraped_text.splitlines(False)):
                    if n < max_linhas:
                        textobject.textLine(line.rstrip())
                pdf.drawText(textobject)

            if vertical >= 0 and horizontal > 0:
                parc = str(dados['imoveis']['parcelas'][((pag_n - 1) * dados["imov_qtd"]) + vertical][horizontal - 1])
                wraped_text = "\n".join(wrap(parc, text_wrap_parc))
                textobject = pdf.beginText(inicia_em_h + y + espacamento_h,
                                           pag_alt - inicia_em_v - x - (espacamento_v - 3))

                se_ativo = dados['imoveis']['parcelas_ativas'][((pag_n - 1) * dados["imov_qtd"]) + vertical][
                    horizontal - 1]
                if se_ativo is True:
                    textobject.setFillColor(colors.black)
                else:
                    textobject.setFillColor(colors.gray)

                textobject.setFont('Times-Roman', text_tam_parc)
                textobject.setCharSpace(char_space)
                textobject.setLeading(leading)
                for line in wraped_text.splitlines(False):
                    textobject.textLine(line.rstrip())
                pdf.drawText(textobject)

                sinal = str(dados['imoveis']['sinais'][((pag_n - 1) * dados["imov_qtd"]) + vertical][horizontal - 1])
                textobject = pdf.beginText(inicia_em_h + y + celula_largura - espacamento_h - espac_h_sinal,
                                           pag_alt - inicia_em_v - x - text_tam_parc)
                textobject.setFillColor(colors.blue)

                if sinal == 'Ok':
                    # Ok
                    textobject.setFillColor(HexColor(0x354c70))
                elif sinal == 'Re':
                    # Falta recibo
                    textobject.setFillColor(HexColor(0xCEAD4D))
                elif sinal == 'Ve':
                    # Venceu
                    textobject.setFillColor(HexColor(0x8D0000))

                textobject.setFont('Times-Roman', text_tam_parc)
                textobject.setCharSpace(char_space)
                textobject.setLeading(leading)
                textobject.textLine(sinal.rstrip())
                pdf.drawText(textobject)

    return {'celula_altura': celula_altura}


def gerar_tabela_pdf(dados):
    # Preparando o PDF:
    local = f'{settings.MEDIA_ROOT}/tabela_docs/tabela_{dados["session_key"]}_{dados["usuario"]}.pdf'
    a4h = (297 * mm, 210 * mm)
    pdf = canvas.Canvas(local, pagesize=a4h)

    paginas = int((len(dados['imoveis']['nomes'])) / dados['imov_qtd']) if (len(dados['imoveis']['nomes'])) / dados[
        'imov_qtd'] % 2 == 1 else ceil((len(dados['imoveis']['nomes'])) / dados['imov_qtd'])
    ultima = len(dados['imoveis']['nomes']) - ((paginas - 1) * dados['imov_qtd'])
    fazer = dados['imov_qtd']

    infos = {'celula_altura': 100}
    for pagina in range(0, paginas):
        if pagina == paginas - 1:
            fazer = ultima
        pag_n = pdf.getPageNumber()
        infos = criar_uma_pagina_tabela(fazer=fazer, pag_n=pag_n, a4h=a4h, dados=dados, pdf=pdf,
                                        celula_altura=infos['celula_altura'])
        pdf.showPage()

    pdf.setCreator(settings.SITE_URL)
    pdf.setAuthor(f'{dados["usuario_nome_compl"]}')
    pdf.setTitle(f'Tabela de agenda dos imóveis de {dados["usuario_username"]}')
    pdf.setSubject(f'Tabela completa com a agenda dos imóveis ativos.')

    pdf.save()


# 102: -----------------------------------------------
modelo_variaveis = {
    0: ['[!variavel: semana_extenso_hoje]', 'Dia da semana hoje escrito por extenso'],
    64: ['[!variavel: data_extenso_hoje]', 'Dia, mês e ano de hoje escritos por extenso'],
    1: ['[!variavel: data_hoje]', 'Data abreviada de hoje'],
    43: ['[!variavel: tipo_de_locacao]', 'Locação residencial ou locação comercial/industrial'],
    49: ['[!variavel: caucao]', 'Valor da caução/depósito a ser pago'],
    50: ['[!variavel: caucao_por_extenso]', 'Valor da caução/depósito a ser pago por extenso'],

    2: ['[!variavel: locador_nome_completo]', 'Nome completo do locador do imóvel deste contrato'],
    3: ['[!variavel: locador_nacionalidade]', 'Nacionalidade do locador do imóvel deste contrato'],
    4: ['[!variavel: locador_estado_civil]', 'Estado civil do locador do imóvel deste contrato'],
    5: ['[!variavel: locador_ocupacao]', 'Ocupação trabalhista do locador do imóvel deste contrato'],
    6: ['[!variavel: locador_rg]', 'Documento número de RG do locador do imóvel deste contrato'],
    7: ['[!variavel: locador_cpf]', 'Documento número de CPF do locador do imóvel deste contrato'],
    63: ['[!variavel: locador_telefone]', 'Número do telefone celular do locador do imóvel deste contrato'],
    8: ['[!variavel: locador_endereco_completo]', 'Endereço completo do locador do imóvel deste contrato'],
    47: ['[!variavel: locador_email]', 'Endereço de e-mail do locador do imóvel deste contrato'],
    32: ['[!variavel: locador_pagamento_1]', 'Informações de pagamento 1 do locador do imóvel deste contrato'],
    33: ['[!variavel: locador_pagamento_2]', 'Informações de pagamento 2 do locador do imóvel deste contrato'],

    9: ['[!variavel: imovel_rotulo]', 'Rótulo do imóvel deste contrato'],
    44: ['[!variavel: imovel_grupo]', 'Grupo no qual o imóvel deste contrato está inserido'],
    10: ['[!variavel: imovel_uc_energia]', 'Unidade consumidora de energia do imóvel deste contrato'],
    11: ['[!variavel: imovel_uc_sanemameto]', 'Unidade consumidora de saneamento do imóvel deste contrato'],
    12: ['[!variavel: imovel_cidade]', 'Cidade onde se localiza o imóvel deste contrato'],
    48: ['[!variavel: imovel_estado]', 'Estado onde se localiza o imóvel deste contrato'],
    62: ['[!variavel: imovel_bairro]', 'Bairro onde se localiza o imóvel deste contrato'],
    13: ['[!variavel: imovel_endereco_completo]', 'Endereço completo do imóvel deste contrato'],
    61: ['[!variavel: imovel_grupo_tipo]', 'Tipo de grupo no qual o imóvel deste contrato está inserido'],

    14: ['[!variavel: locatario_nome_completo]', 'Nome completo do locatário do imóvel deste contrato'],
    15: ['[!variavel: locatario_cpf]', 'Documento número de CPF do locatário do imóvel deste contrato'],
    16: ['[!variavel: locatario_rg]', 'Documento número de RG do locatário do imóvel deste contrato'],
    17: ['[!variavel: locatario_nacionalidade]', 'Nacionalidade do locatário do imóvel deste contrato'],
    18: ['[!variavel: locatario_estado_civil]', 'Estado civil do locatário do imóvel deste contrato'],
    19: ['[!variavel: locatario_ocupacao]', 'Ocupação trabalhista do locatário do imóvel deste contrato'],
    52: ['[!variavel: locatario_endereco_completo]', 'Endereço completo do locatário do imóvel deste contrato'],
    20: ['[!variavel: locatario_celular_1]', 'Número de celular 1 do locatário do imóvel deste contrato'],
    21: ['[!variavel: locatario_celular_2]', 'Número de celular 2 do locatário do imóvel deste contrato'],
    42: ['[!variavel: locatario_email]', 'Endereço de e-mail do locatário do imóvel deste contrato'],

    36: ['[!variavel: fiador_nome_completo]', 'Nome completo do fiador do imóvel deste contrato'],
    37: ['[!variavel: fiador_rg]', 'Documento número de RG do fiador do imóvel deste contrato'],
    38: ['[!variavel: fiador_cpf]', 'Documento número de CPF do fiador do imóvel deste contrato'],
    51: ['[!variavel: fiador_endereco_completo]', 'Endereço completo do fiador do imóvel deste contrato'],
    39: ['[!variavel: fiador_ocupacao]', 'Ocupação trabalhista do fiador do imóvel deste contrato'],
    40: ['[!variavel: fiador_nacionalidade]', 'Nacionalidade do fiador do imóvel deste contrato'],
    41: ['[!variavel: fiador_estado_civil]', 'Estado civil do fiador do imóvel deste contrato'],

    22: ['[!variavel: contrato_data_entrada]', 'Data de entrada do locatário no imóvel'],
    23: ['[!variavel: contrato_data_saida]', 'Data de saída do locatário no imóvel'],
    24: ['[!variavel: contrato_codigo]', 'Código do contrato'],
    25: ['[!variavel: contrato_periodo]', 'Período de validade, em meses, de validade do contrato'],
    26: ['[!variavel: contrato_periodo_por_extenso]',
         'Período de validade, em meses, de validade do contrato, por extenso'],
    27: ['[!variavel: contrato_parcela_valor]', 'Valor da mensalidade do aluguel'],
    28: ['[!variavel: contrato_parcela_valor_por_extenso]', 'Valor da mensalidade do aluguel, por extenso'],
    45: ['[!variavel: contrato_valor_total]', 'Valor total do contrato, todas as parcelas juntas'],
    46: ['[!variavel: contrato_valor_total_por_extenso]', 'Valor total do contrato, por extenso'],
    34: ['[!variavel: contrato_vencimento]', 'Dia de vencimento do pagamento da mensalidade do aluguel'],
    35: ['[!variavel: contrato_vencimento_por_extenso]',
         'Dia de vencimento do pagamento da mensalidade do aluguel, por extenso'],

    29: ['[!variavel: contrato_anterior-codigo]',
         'Código do contrato anterior deste locatário, neste imóvel'],
    30: ['[!variavel: contrato_anterior-data_entrada]',
         'Data de entrada do locatário do imóvel do contrato anterior'],
    31: ['[!variavel: contrato_anterior-data_saida]',
         'Data de saída do locatário do imóvel do contrato anterior'],
    53: ['[!variavel: contrato_anterior-parcela_valor]',
         'Valor da mensalidade do aluguel do contrato anterior'],
    54: ['[!variavel: contrato_anterior-parcela_valor_por_extenso]',
         'Valor da mensalidade do aluguel do contrato anterior, por extenso'],
    55: ['[!variavel: contrato_anterior_valor_total]',
         'Valor total do contrato anterior, todas as parcelas juntas'],
    56: ['[!variavel: contrato_anterior_valor_total_por_extenso]',
         'Valor total do contrato anterior, por extenso'],
    57: ['[!variavel: contrato_anterior_vencimento]',
         'Dia de vencimento do pagamento da mensalidade do aluguel do contrato anterior'],
    58: ['[!variavel: contrato_anterior_vencimento_por_extenso]',
         'Dia de vencimento do pagamento da mensalidade do aluguel do contrato anterior, por extenso'],
    59: ['[!variavel: contrato_anterior-periodo]',
         'Período de validade, em meses, de validade do contrato anterior'],
    60: ['[!variavel: contrato_anterior-periodo_por_extenso]',
         'Período de validade, em meses, de validade do contrato anterior, por extenso'],
}

modelo_condicoes = {
    0: ['[!condicao: fiador_existe]', 'Mostrar trecho caso exista dados do fiador'],
    1: ['[!condicao: fiador_nao_existe]', 'Mostrar trecho caso não exista dados do fiador'],
    2: ['[!condicao: tipo_residencial]', 'Mostrar trecho caso o tipo de contrato é residencial'],
    3: ['[!condicao: tipo_nao_residencial]', 'Mostrar trecho caso o tipo de contrato é comercial/industrial'],
    4: ['[!condicao: imovel_grupo_Casa]', 'Mostrar trecho caso o imóvel pertença à um grupo do tipo Casa'],
    5: ['[!condicao: imovel_grupo_Apartamento]',
        'Mostrar trecho caso o imóvel pertença à um grupo do tipo Apartamento'],
    6: ['[!condicao: imovel_grupo_Kitnet]', 'Mostrar trecho caso o imóvel pertença à um grupo do tipo Kitnet'],
    7: ['[!condicao: imovel_grupo_Box/Loja]', 'Mostrar trecho caso o imóvel pertença à um grupo do tipo Box/Loja'],
    8: ['[!condicao: imovel_grupo_Escritório]', 'Mostrar trecho caso o imóvel pertença à um grupo do tipo Escritório'],
    9: ['[!condicao: imovel_grupo_Depósito/Armazém]',
        'Mostrar trecho caso o imóvel pertença à um grupo do tipo Depósito/Armazém'],
    10: ['[!condicao: imovel_grupo_Galpão]', 'Mostrar trecho caso o imóvel pertença à um grupo do tipo Galpão'],
    11: ['[!condicao: contrato_anterior_existe]',
         'Mostrar trecho caso exista um contrato anterior à este com este locador neste imóvel'],
    12: ['[!condicao: contrato_anterior_nao_existe]',
         'Mostrar trecho caso não exista um contrato anterior à este com este locador neste imóvel'],
}


def gerar_contrato_pdf(dados, visualizar=False):
    # Gerar modelo em pdf e salvar em media/contrato_docs para ser carregado pela view'
    # Criar a pasta contrato_docs se não existe
    modelo_corpo = dados['modelo'].corpo

    if visualizar:
        pasta = rf'{settings.MEDIA_ROOT}/contratos_modelos/'
        se_existe = os.path.exists(pasta)
        if not se_existe:
            os.makedirs(pasta)
        local = f'contratos_modelos/user_{dados["usuario_username"]}-modelo_{dados["modelo_pk"]}.pdf'
    else:
        pasta = rf'{settings.MEDIA_ROOT}/contrato_docs/'
        se_existe = os.path.exists(pasta)
        if not se_existe:
            os.makedirs(pasta)
        local = f'contrato_docs/contrato_{dados["session_key"]}_{dados["usuario"]}.pdf'

    if visualizar is False:
        # Capturar trechos de cada condição registrada em modelo_condicoes
        for i, j in modelo_condicoes.items():
            # Aqui colocaremos no objeto posições cada trecho do item atual de modelo_condicoes(caso haja, senão aviso)
            comando_inicio = j[0]
            comando_fim = f'{comando_inicio[:comando_inicio.find("]")]}_fim{comando_inicio[comando_inicio.find("]"):]}'
            indice = 0

            while indice < len(modelo_corpo):
                indice = modelo_corpo.find(j[0], indice)
                if indice == -1:
                    break
                pos_fim = modelo_corpo[indice:].find(comando_fim)
                trecho = modelo_corpo[indice:indice + pos_fim + len(comando_fim)]
                tem_comando_fim = True if comando_fim in trecho else False
                trecho_final = trecho[len(comando_inicio):-len(comando_fim)]

                # Funções das condições:
                # Economizar processamento, se necessário: Evitar essa busca de texto, e sim, enviar um parâmetro \/
                if comando_inicio == '[!condicao: fiador_existe]' and tem_comando_fim:
                    if '[ESTE DADO DO FIADOR NÃO FOI PREENCHIDO]' in dados['fiador_nome_completo']:
                        modelo_corpo = modelo_corpo.replace(trecho, '')
                    else:
                        modelo_corpo = modelo_corpo.replace(trecho, trecho_final)

                if comando_inicio == '[!condicao: fiador_nao_existe]' and tem_comando_fim:
                    if '[ESTE DADO DO FIADOR NÃO FOI PREENCHIDO]' in dados['fiador_nome_completo']:
                        modelo_corpo = modelo_corpo.replace(trecho, trecho_final)
                    else:
                        modelo_corpo = modelo_corpo.replace(trecho, '')

                if comando_inicio == '[!condicao: tipo_residencial]' and tem_comando_fim:
                    if dados['tipo_de_locacao'] == 'residencial':
                        modelo_corpo = modelo_corpo.replace(trecho, trecho_final)
                    else:
                        modelo_corpo = modelo_corpo.replace(trecho, '')

                if comando_inicio == '[!condicao: tipo_nao_residencial]' and tem_comando_fim:
                    if dados['tipo_de_locacao'] == 'não residencial':
                        modelo_corpo = modelo_corpo.replace(trecho, trecho_final)
                    else:
                        modelo_corpo = modelo_corpo.replace(trecho, '')

                if comando_inicio == '[!condicao: imovel_grupo_Casa]' and tem_comando_fim:
                    if dados['imovel_grupo_tipo'] == 'Casa':
                        modelo_corpo = modelo_corpo.replace(trecho, trecho_final)
                    else:
                        modelo_corpo = modelo_corpo.replace(trecho, '')

                if comando_inicio == '[!condicao: imovel_grupo_Apartamento]' and tem_comando_fim:
                    if dados['imovel_grupo_tipo'] == 'Apartamento':
                        modelo_corpo = modelo_corpo.replace(trecho, trecho_final)
                    else:
                        modelo_corpo = modelo_corpo.replace(trecho, '')

                if comando_inicio == '[!condicao: imovel_grupo_Kitnet]' and tem_comando_fim:
                    if dados['imovel_grupo_tipo'] == 'Kitnet':
                        modelo_corpo = modelo_corpo.replace(trecho, trecho_final)
                    else:
                        modelo_corpo = modelo_corpo.replace(trecho, '')

                if comando_inicio == '[!condicao: imovel_grupo_Box/Loja]' and tem_comando_fim:
                    if dados['imovel_grupo_tipo'] == 'Box/Loja':
                        modelo_corpo = modelo_corpo.replace(trecho, trecho_final)
                    else:
                        modelo_corpo = modelo_corpo.replace(trecho, '')

                if comando_inicio == '[!condicao: imovel_grupo_Escritório]' and tem_comando_fim:
                    if dados['imovel_grupo_tipo'] == 'Escritório':
                        modelo_corpo = modelo_corpo.replace(trecho, trecho_final)
                    else:
                        modelo_corpo = modelo_corpo.replace(trecho, '')

                if comando_inicio == '[!condicao: imovel_grupo_Depósito/Armazém]' and tem_comando_fim:
                    if dados['imovel_grupo_tipo'] == 'Depósito/Armazém':
                        modelo_corpo = modelo_corpo.replace(trecho, trecho_final)
                    else:
                        modelo_corpo = modelo_corpo.replace(trecho, '')

                if comando_inicio == '[!condicao: imovel_grupo_Galpão]' and tem_comando_fim:
                    if dados['imovel_grupo_tipo'] == 'Galpão':
                        modelo_corpo = modelo_corpo.replace(trecho, trecho_final)
                    else:
                        modelo_corpo = modelo_corpo.replace(trecho, '')

                if comando_inicio == '[!condicao: contrato_anterior_existe]' and tem_comando_fim:
                    if '[NÃO EXISTE CONTRATO ANTERIOR A ESTE]' in dados['contrato_anterior-codigo']:
                        modelo_corpo = modelo_corpo.replace(trecho, '')
                    else:
                        modelo_corpo = modelo_corpo.replace(trecho, trecho_final)

                if comando_inicio == '[!condicao: contrato_anterior_nao_existe]' and tem_comando_fim:
                    if '[NÃO EXISTE CONTRATO ANTERIOR A ESTE]' in dados['contrato_anterior-codigo']:
                        modelo_corpo = modelo_corpo.replace(trecho, trecho_final)
                    else:
                        modelo_corpo = modelo_corpo.replace(trecho, '')

                # Fim das funções das condições
                indice += 1

        # Aplicar Variaveis \/
        for i, j in modelo_variaveis.items():
            modelo_corpo = modelo_corpo.replace(j[0], dados[f"{j[0][j[0].find(': ') + 2:-1]}"])

    with open(fr"{settings.MEDIA_ROOT}/{local}", "wb") as f:
        pisa.CreatePDF(modelo_corpo, dest=f, )
    f.close()

    if visualizar:
        return local
