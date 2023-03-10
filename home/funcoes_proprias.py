import io
from math import ceil
from textwrap import wrap

from django.core.exceptions import ValidationError

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.colors import HexColor

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

# eu ia fazer uma funçao aqui, nçao precisei mais

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
        f'<BR/>{dados["data_preenchimento"][recibo_n-1]}</i><BR/><BR/><BR/>'
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
def gerar_recibos(dados):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setAuthor(f'{dados["nome_locador"]}')
    pdf.setTitle(f'Recibos do contrato {dados["cod_contrato"]}')
    pdf.setCreator(settings.SITE_LINK)
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
            dados['data_preenchimento'].append("________________, ____ de ____________ de ________")

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
    media_alt_larg = round(((celula_altura+celula_largura)/2))

    # print('celula_altura: ', celula_altura, 'celula_largura: ', celula_largura, 'media: ', media_alt_larg)

    # Encaixe de texto
    text_wrap_imo = espacamento_h = espacamento_v = text_tam_imo = text_wrap_parc = text_tam_parc = leading = 0

    # Verticalmente (leading)
    if celula_altura <= 61:
        leading = 8.5  # 9 10.5
        espacamento_v = 11  # 12 13
    elif celula_altura <= 76:
        leading = 9
        espacamento_v = 12
    elif celula_altura <= 92:
        leading = 10.5
        espacamento_v = 13

    # Horizontalmente  (wrap)
    if celula_largura <= 104:
        text_wrap_imo = 18
        text_wrap_parc = 30
        espacamento_h = 2
    elif celula_largura <= 135:
        text_wrap_imo = 20
        text_wrap_parc = 32
        espacamento_h = 2
    elif celula_largura <= 167:
        text_wrap_imo = 22
        text_wrap_parc = 33
        espacamento_h = 4

    # media (tam)
    if media_alt_larg <= 82:
        text_tam_imo = 10
        text_tam_parc = 7
    elif media_alt_larg <= 106:
        text_tam_imo = 11
        text_tam_parc = 7
    elif media_alt_larg <= 130:
        text_tam_imo = 14
        text_tam_parc = 10

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
                textobject.setFont('Times-Roman', 11)
                textobject.textLine(
                    f'Tabela de agenda dos imóveis de '
                    f'{dados["usuario_username"]} (De {dados["datas"][0]} Até {dados["datas"][-1]})')
                pdf.drawText(textobject)

                textobject = pdf.beginText(inicia_em_h + y,
                                           pag_alt - inicia_em_v - celula_altura - x + celula_altura + 2)
                textobject.setFillColor(colors.black)
                textobject.setFont('Impact', 12)
                textobject.textLine('Imóveis Ativos')
                pdf.drawText(textobject)

            if vertical == 0 and horizontal > 0:
                textobject = pdf.beginText(inicia_em_h + y,
                                           pag_alt - inicia_em_v - celula_altura - x + celula_altura + 2)
                textobject.setFillColor(colors.black)
                textobject.setFont('Impact', 12)
                textobject.textLine(f'{dados["datas"][horizontal - 1]}')
                pdf.drawText(textobject)

            if vertical >= 0 and horizontal == 0:
                mytext = f'{dados["imoveis_nomes"][((pag_n - 1) * dados["imov_qtd"]) + vertical]}'
                wraped_text = "\n".join(wrap(mytext, text_wrap_imo))
                textobject = pdf.beginText(inicia_em_h + y + espacamento_h,
                                           pag_alt - inicia_em_v - x - espacamento_v)
                textobject.setFillColor(colors.black)
                textobject.setFont('Arial', text_tam_imo)
                for line in wraped_text.splitlines(False):
                    textobject.textLine(line.rstrip())
                pdf.drawText(textobject)

            if vertical >= 0 and horizontal > 0:
                parc = str(dados['parcelas'][((pag_n - 1) * dados["imov_qtd"]) + vertical][horizontal - 1])
                wraped_text = "\n".join(wrap(parc, text_wrap_parc))
                textobject = pdf.beginText(inicia_em_h + y + espacamento_h,
                                           pag_alt - inicia_em_v - x - (espacamento_v - 3))
                textobject.setFillColor(colors.gray)
                textobject.setFont('Arial', text_tam_parc)
                textobject.setCharSpace(0.4)
                textobject.setLeading(leading)
                for line in wraped_text.splitlines(False):
                    textobject.textLine(line.rstrip())
                pdf.drawText(textobject)

                sinal = str(dados['sinais'][((pag_n - 1) * dados["imov_qtd"]) + vertical][horizontal - 1])
                textobject = pdf.beginText(inicia_em_h + y + celula_largura - espacamento_h - 8,
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

                textobject.setFont('Impact', text_tam_parc)
                textobject.setCharSpace(0.4)
                textobject.setLeading(leading)
                textobject.textLine(sinal.rstrip())
                pdf.drawText(textobject)

    return {'celula_altura': celula_altura}


def gerar_tabela(dados):
    # Preparando o PDF:
    local = f'{settings.MEDIA_ROOT}tabela_docs/tabela_{dados["usuario_uuid"]}_{dados["usuario"]}.pdf'
    a4h = (297 * mm, 210 * mm)
    pdf = canvas.Canvas(local, pagesize=a4h)
    pdfmetrics.registerFont(TTFont('Impact', 'Impact.ttf'))
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))

    paginas = int((len(dados['imoveis_nomes'])) / dados['imov_qtd']) if (len(dados['imoveis_nomes'])) / dados[
        'imov_qtd'] % 2 == 1 else ceil((len(dados['imoveis_nomes'])) / dados['imov_qtd'])
    ultima = len(dados['imoveis_nomes']) - ((paginas - 1) * dados['imov_qtd'])
    fazer = dados['imov_qtd']

    infos = {'celula_altura': 100}
    for pagina in range(0, paginas):
        if pagina == paginas - 1:
            fazer = ultima
        pag_n = pdf.getPageNumber()
        infos = criar_uma_pagina_tabela(fazer=fazer, pag_n=pag_n, a4h=a4h, dados=dados, pdf=pdf,
                                        celula_altura=infos['celula_altura'])
        pdf.showPage()

    pdf.setCreator(settings.SITE_LINK)
    pdf.setAuthor(f'{dados["usuario_nome_compl"]}')
    pdf.setTitle(f'Tabela de agenda dos imóveis de {dados["usuario_username"]}')
    pdf.setSubject(f'Tabela completa com a agenda dos imóveis ativos.')

    pdf.save()
