from math import ceil
import io

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

from django.http import FileResponse


# 001: -----------------------------------------------
def valor_br(valor):
    """ O valor deve ser inteiro e vir em format string e será convertido para valor financeiro em Reais(R$) onde as
    duas últimas casas sempre representarão centavos Ex: de 134567899 para 1.345.678,99"""
    virgola = str(',') if int(valor) > 99 else str('0,')
    y = '' if int(valor) < 100 else f'{int(valor[:-2]):_.2f}'.replace('_', '.')
    z = f'{y[:-3]}{virgola}{str(valor)[-2:]}'
    return f'R${z}'


# 002: -----------------------------------------------

def gerar_um_recibo(pdf, pag_lar, pag_centro, recibo_n, pos_y, dados, parcelas):
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

    texto_estilo = ParagraphStyle('My Para style', fontName='Times-Roman', fontSize=11, borderPadding=(20, 20, 20),
                                  leading=14, alignment=1)
    texto = Paragraph(
        f'Eu, <b>{dados["nome_locador"]}</b>, inscrito no RG sob o nº {dados["rg_locd"]}'
        f' e CPF sob o nº {dados["cpf_locd"]}, recebi de <b>{dados["nome_locatario"]}</b>,'
        f' inscrito(a) no RG sob o nº {dados["rg_loct"]} e CPF sob o n° {dados["cpf_loct"]},'
        f' a importância de <b>{dados["valor_e_extenso"]}</b>, referente ao pagamento do aluguel'
        f' do mês de <b>{dados["mes_e_ano"][2 * (recibo_n - 1)]} DE '
        f'{dados["mes_e_ano"][(2 * (recibo_n - 1)) + 1]}</b> (Parcela {recibo_n} de um total '
        f'de {parcelas}), de um imóvel localizado no endereço: {dados["endereco"]}, declarando '
        f'portanto, plena, total e irrevogável quitação do mês referido a partir de então.'
        f' <BR/><BR/><i> Para maior clareza firmo o presente em<BR/><BR/>{dados["cidade"]},'
        f' {dados["data"]}.</i><BR/><BR/><BR/>'
        f'___________________________________________________________________________________'
        f'<BR/>{dados["nome_locador"]}',
        texto_estilo)
    texto.wrapOn(pdf, 525, 110)
    texto.drawOn(pdf, rect_pos_x + 5, rect_pos_y + 15)


def gerar_uma_pagina(pdf, parcelas, pag_centro, pag_alt, pag_lar, pag_n, dados):
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

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setAuthor(f'{dados["nome_locador"]}')
    pdf.setTitle(f'Recibos do contrato {dados["cod_contrato"]} página 1')
    pdf.setCreator('www.administradordelocacao.com.br')
    pdf.setSubject(f'Recibos do contrato {dados["cod_contrato"]}')

    pag_lar = A4[0]
    pag_alt = A4[1]
    pag_centro = (pag_lar / 2, pag_alt / 2)

    parcelas = int(len(dados['mes_e_ano']) / 2)
    paginas = int((len(dados['mes_e_ano']) / 2) / 3) if (len(dados['mes_e_ano']) / 2) / 3 % 2 == 1 else ceil(
        (len(dados['mes_e_ano']) / 2) / 3)

    for pagina in range(paginas):
        page_num = pdf.getPageNumber()
        gerar_uma_pagina(pag_n=page_num, pag_alt=pag_alt, pag_centro=pag_centro, pag_lar=pag_lar,
                         parcelas=parcelas, dados=dados, pdf=pdf)
        pdf.showPage()

    pdf.save()
    buffer.seek(0)
    return buffer
