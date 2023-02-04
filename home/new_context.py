from Adm_de_Locacao import settings

from django.urls import resolve

from home.forms import FormMensagem, FormAdmin
from home.forms import FormPagamento, FormGasto, FormLocatario, FormContrato, FormImovel, FormAnotacoes


def titulo_pag(request):
    titulo = resolve(request.path_info).url_name
    if settings.DEBUG:
        debug = resolve(request.path_info)
        return {'block_titulo': titulo, 'pageinfo': debug}
    return {'block_titulo': titulo}


def forms_da_navbar(request):
    if request.user.is_authenticated:

        if request.session.get('form1'):
            form1 = FormPagamento(request.user, request.session.get('form1'))
        else:
            form1 = FormPagamento(request.user)

        if request.session.get('form2'):
            form2 = FormMensagem(request.session.get('form2'))
        else:
            form2 = FormMensagem()

        if request.session.get('form3'):
            form3 = FormGasto(request.session.get('form3'))
        else:
            form3 = FormGasto()

        if request.session.get('form4'):
            form4 = FormLocatario(request.session.get('form4'))
        else:
            form4 = FormLocatario()

        if request.session.get('form5'):
            form5 = FormContrato(request.user, request.session.get('form5'))
        else:
            form5 = FormContrato(request.user)

        if request.session.get('form6'):
            form6 = FormImovel(request.user, request.session.get('form6'))
        else:
            form6 = FormImovel(request.user)

        if request.session.get('form7'):
            form7 = FormAnotacoes(request.session.get('form7'))
        else:
            form7 = FormAnotacoes()

        form8 = FormAdmin()

        context = {'form_pagamento': form1, 'form_mensagem': form2, 'form_gasto': form3, 'form_locatario': form4,
                   'form_contrato': form5, 'form_imovel': form6, 'form_notas': form7, 'botao_admin': form8}

        return context
    else:
        context = {}
        return context
