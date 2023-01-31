import os
import random
import string
import locale
from datetime import datetime
from dateutil.relativedelta import relativedelta

from Adm_de_Locacao.settings import MEDIA_ROOT
from django.db.models.signals import pre_delete, post_save, pre_save
from django.dispatch import receiver
from num2words import num2words

from home.models import Contrato, Imovei, Locatario, Usuario, Recibo
from home.funcoes_proprias import gerar_recibos
from home.models import Recibo


@receiver(pre_delete, sender=Contrato)
def contrato_delete(sender, instance, **kwards):
    # Pega os dados para tratamento:
    contrato = Contrato.objects.get(pk=instance.pk)
    imovel = Imovei.objects.get(pk=contrato.do_imovel.pk)
    locatario = Locatario.objects.get(pk=contrato.do_locatario.pk)

    # Remove locador do imovel quando deleta um contrato
    if imovel.com_locatario is True:
        locatario.com_imoveis.remove(imovel)
        locatario.com_contratos.remove(contrato)
        imovel.com_locatario = None
        imovel.contrato_atual = None
        imovel.save()
        locatario.save()

    # Remove o arquivo 'Recibos' corerspndente quando deleta um contrato
    # (a fazer) ------------<


@receiver(post_save, sender=Contrato)
def contrato_update(sender, instance, created, **kwargs):
    # Pega os dados para tratamento:
    contrato = Contrato.objects.get(pk=instance.pk)
    imovel = Imovei.objects.get(pk=contrato.do_imovel.pk)
    usuario = Usuario.objects.get(pk=contrato.do_locador.pk)
    local = ''

    # Remove locador do imovel quando um contrato fica inativo e adiciona quando fica ativo:
    locatario = Locatario.objects.get(pk=contrato.do_locatario.pk)
    if contrato.em_posse is True and contrato.rescindido is False and contrato.vencido is False:
        locatario.com_imoveis.add(imovel)
        locatario.com_contratos.add(contrato)
        imovel.com_locatario = locatario
        imovel.contrato_atual = contrato
        imovel.save()
        locatario.save()
    else:
        locatario.com_imoveis.remove(imovel)
        locatario.com_contratos.remove(contrato)
        imovel.com_locatario = None
        imovel.contrato_atual = None
        imovel.save()
        locatario.save()

    if created:
        # Gera os recibos quando o contrato é criado:
        for x in range(0, contrato.duracao):
            data_entrada = contrato.data_entrada
            data = data_entrada.replace(day=contrato.dia_vencimento) + relativedelta(months=x)

            codigos_existentes = list(
                Recibo.objects.filter(do_contrato=contrato.pk).values("codigo").values_list('codigo', flat=True))
            while True:
                recibo_codigo = ''.join(
                    random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in
                    range(6))
                if recibo_codigo not in codigos_existentes:
                    Recibo.objects.create(do_contrato=contrato, data_pagm_ref=data,
                                          codigo=f'{recibo_codigo[:3]}-{recibo_codigo[3:]}')
                    break

        # Preencher o campo recibos_pdf de contrato com o link do arquivo de recibos
        locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
        month = str(datetime.today().strftime('%B'))
        year = str(datetime.today().strftime('%Y'))

        if not os.path.exists(rf'{MEDIA_ROOT}/recibos_docs/{year}/{month}/'):
            os.makedirs(rf'{MEDIA_ROOT}/recibos_docs/{year}/{month}/')

        local = f'recibos_docs/{year}/{month}/{locatario.nome} - {contrato.codigo}.pdf'

        contrato.recibos_pdf = local
        # contrato.save(update_fields=['recibos_pdf'])

    # Modificar os recibos quando o contrato é criado ou modificado:
    reais = int(contrato.valor_mensal[:-2])
    centavos = int(contrato.valor_mensal[-2:])
    num_ptbr_reais = num2words(reais, lang='pt-br')
    completo = ''
    if centavos > 0:
        num_ptbr_centavos = num2words(centavos, lang='pt-br')
        completo = f' E {num_ptbr_centavos} centavos'
    codigos = list(Recibo.objects.filter(do_contrato=contrato.pk).values("codigo").values_list('codigo', flat=True))
    datas = list(
        Recibo.objects.filter(do_contrato=contrato.pk).values("data_pagm_ref").values_list('data_pagm_ref', flat=True))
    datas_tratadas = list()
    for data in datas:
        locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
        month = data.strftime('%B')
        year = data.strftime('%Y')
        datas_tratadas.append(f'{month.upper()}')
        datas_tratadas.append(f'{year}')

    dados = {'cod_contrato': f'{contrato.codigo}',
             'nome_locador': f'{usuario.first_name.upper()} {usuario.last_name.upper()}',
             'rg_locd': f'{usuario.RG}',
             'cpf_locd': f'{usuario.CPF}',
             'nome_locatario': f'{locatario.nome.upper()}',
             'rg_loct': f'{locatario.RG}',
             'cpf_loct': f'{locatario.CPF}',
             'valor_e_extenso': f'{contrato.valor_br()} ({num_ptbr_reais.upper()} REAIS{completo.upper()})',
             'endereco': f"{imovel.endereco}",
             'cidade': f'{imovel.cidade}',
             'data': '________________, ____ de _________ de ________',
             'cod_recibo': codigos,
             'mes_e_ano': datas_tratadas,
             }

    gerar_recibos(dados=dados, local=local)
