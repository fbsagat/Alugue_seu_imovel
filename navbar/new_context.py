from Adm_de_Locacao import settings
from django.urls import resolve
from home.forms import FormMensagem, FormAdmin
from navbar.forms import FormPagamento, FormGasto, FormLocatario, FormContrato, FormImovel, FormAnotacoes


def titulo_pag(request):
    titulo = resolve(request.path_info).url_name
    if settings.DEBUG:
        debug = resolve(request.path_info)
        return {'block_titulo': titulo, 'pageinfo': debug}
    return {'block_titulo': titulo}


def forms_da_navbar(request):
    if request.user.is_authenticated:
        form1 = FormPagamento(request.user)
        form2 = FormMensagem()
        form3 = FormGasto()
        form4 = FormLocatario()
        form5 = FormContrato(request.user)
        form6 = FormImovel(request.user)
        form7 = FormAnotacoes()
        form8 = FormAdmin()

        context = {'form_pagamento': form1, 'form_mensagem': form2, 'form_gasto': form3, 'form_locatario': form4,
                   'form_contrato': form5, 'form_imovel': form6, 'form_notas': form7, 'botao_admin': form8}
        return context
    else:
        context = {}
        return context
