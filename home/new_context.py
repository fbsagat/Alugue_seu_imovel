import datetime
from datetime import timedelta

from Alugue_seu_imovel import settings

from django.urls import resolve

from home.models import Tarefa
from home.forms import FormMensagem, FormAdmin
from home.forms import FormPagamento, FormGasto, FormLocatario, FormContrato, FormImovel, FormAnotacoes
from home.models import Contrato


def titulo_pag(request):
    titulo = resolve(request.path_info).url_name
    ano_atual = datetime.date.today().year
    if settings.DEBUG:
        return {'block_titulo': titulo, 'ano_atual': ano_atual, 'debug_true': True}
    return {'block_titulo': titulo, 'ano_atual': ano_atual}


def forms_da_navbar(request):
    if request.user.is_authenticated:
        # Apenas contratos ativos hoje ou futuramente para os forms
        contratos_exibir = Contrato.objects.ativos_margem().filter(do_locador=request.user).order_by('-data_entrada')

        if request.session.get('form1'):
            tempo_form = datetime.datetime.strptime(request.session.get('form1')[1], '%H:%M:%S')
            tempo_agora = datetime.datetime.strptime(datetime.datetime.now().time().strftime('%H:%M:%S'), '%H:%M:%S')

            if tempo_form + timedelta(seconds=settings.TEMPO_SESSION_FORM) > tempo_agora:
                form1 = FormPagamento(request.user, request.session.get('form1')[0])
                form1.fields['ao_contrato'].queryset = contratos_exibir
            else:
                form1 = FormPagamento(request.user,
                                      initial={'data_pagamento': datetime.date.today().strftime('%Y-%m-%d')})
                form1.fields['ao_contrato'].queryset = contratos_exibir
                request.session.pop('form1')
        else:
            form1 = FormPagamento(request.user, initial={'data_pagamento': datetime.date.today().strftime('%Y-%m-%d')})
            form1.fields['ao_contrato'].queryset = contratos_exibir

        if request.session.get('form2'):
            tempo_form = datetime.datetime.strptime(request.session.get('form2')[1], '%H:%M:%S')
            tempo_agora = datetime.datetime.strptime(datetime.datetime.now().time().strftime('%H:%M:%S'), '%H:%M:%S')

            if tempo_form + timedelta(seconds=settings.TEMPO_SESSION_FORM) > tempo_agora:
                form2 = FormMensagem(request.session.get('form2')[0])
            else:
                form2 = FormMensagem()
                request.session.pop('form2')
        else:
            form2 = FormMensagem()

        if request.session.get('form3'):
            tempo_form = datetime.datetime.strptime(request.session.get('form3')[1], '%H:%M:%S')
            tempo_agora = datetime.datetime.strptime(datetime.datetime.now().time().strftime('%H:%M:%S'), '%H:%M:%S')

            if tempo_form + timedelta(seconds=settings.TEMPO_SESSION_FORM) > tempo_agora:
                form3 = FormGasto(request.session.get('form3')[0])
            else:
                form3 = FormGasto(initial={'data': datetime.date.today().strftime('%Y-%m-%d')})
                request.session.pop('form3')
        else:
            form3 = FormGasto(initial={'data': datetime.date.today().strftime('%Y-%m-%d')})

        if request.session.get('form4'):
            tempo_form = datetime.datetime.strptime(request.session.get('form4')[1], '%H:%M:%S')
            tempo_agora = datetime.datetime.strptime(datetime.datetime.now().time().strftime('%H:%M:%S'), '%H:%M:%S')

            if tempo_form + timedelta(seconds=settings.TEMPO_SESSION_FORM) > tempo_agora:
                form4 = FormLocatario(request.session.get('form4')[0], usuario=request.user.pk)
            else:
                form4 = FormLocatario(usuario=request.user.pk)
                request.session.pop('form4')
        else:
            form4 = FormLocatario(usuario=request.user.pk)

        if request.session.get('form5'):
            tempo_form = datetime.datetime.strptime(request.session.get('form5')[1], '%H:%M:%S')
            tempo_agora = datetime.datetime.strptime(datetime.datetime.now().time().strftime('%H:%M:%S'), '%H:%M:%S')

            if tempo_form + timedelta(seconds=settings.TEMPO_SESSION_FORM) > tempo_agora:
                form5 = FormContrato(request.user, request.session.get('form5')[0])
            else:
                form5 = FormContrato(request.user, initial={'data_entrada': datetime.date.today().strftime('%Y-%m-%d')})
                request.session.pop('form5')
        else:
            form5 = FormContrato(request.user, initial={'data_entrada': datetime.date.today().strftime('%Y-%m-%d')})

        if request.session.get('form6'):
            tempo_form = datetime.datetime.strptime(request.session.get('form6')[1], '%H:%M:%S')
            tempo_agora = datetime.datetime.strptime(datetime.datetime.now().time().strftime('%H:%M:%S'), '%H:%M:%S')

            if tempo_form + timedelta(seconds=settings.TEMPO_SESSION_FORM) > tempo_agora:
                form6 = FormImovel(request.user, request.session.get('form6')[0])
            else:
                form6 = FormImovel(request.user)
                request.session.pop('form6')
        else:
            form6 = FormImovel(request.user)

        if request.session.get('form7'):
            tempo_form = datetime.datetime.strptime(request.session.get('form7')[1], '%H:%M:%S')
            tempo_agora = datetime.datetime.strptime(datetime.datetime.now().time().strftime('%H:%M:%S'), '%H:%M:%S')

            if tempo_form + timedelta(seconds=settings.TEMPO_SESSION_FORM) > tempo_agora:
                form7 = FormAnotacoes(request.user, request.session.get('form7')[0])
            else:
                form7 = FormAnotacoes(initial={'data_registro': datetime.date.today().strftime('%Y-%m-%d')})
                request.session.pop('form7')
        else:
            form7 = FormAnotacoes(initial={'data_registro': datetime.date.today().strftime('%Y-%m-%d')})

        if request.user.is_superuser or settings.DEBUG:
            form8 = FormAdmin(
                initial={'qtd_usuario': settings.FICT_QTD['qtd_usuario'],
                         'qtd_locatario': settings.FICT_QTD['qtd_locatario'],
                         'qtd_imovel_g': settings.FICT_QTD['qtd_imovel_g'],
                         'qtd_imovel': settings.FICT_QTD['qtd_imovel'],
                         'qtd_contrato': settings.FICT_QTD['qtd_contrato'],
                         'qtd_pagamento': settings.FICT_QTD['qtd_pagamento'],
                         'qtd_gasto': settings.FICT_QTD['qtd_gasto'], 'qtd_nota': settings.FICT_QTD['qtd_nota'],
                         'qtd_sugestao': settings.FICT_QTD['qtd_sugestao'], 'para_o_usuario': request.user})
        else:
            form8 = ''

        # TAREFAS -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
        tarefas = Tarefa.objects.tarefas_novas().filter(do_usuario=request.user).order_by('-data_registro')
        tarefas_historico = Tarefa.objects.tarefas_historico().filter(do_usuario=request.user).order_by('-data_lida')

        context = {'form_pagamento': form1, 'form_mensagem': form2, 'form_gasto': form3, 'form_locatario': form4,
                   'form_contrato': form5, 'form_imovel': form6, 'form_notas': form7, 'botao_admin': form8,
                   'tarefas': tarefas[:40], 'tarefas_hist': tarefas_historico[:40]}

        return context
    else:
        context = {}
        return context
