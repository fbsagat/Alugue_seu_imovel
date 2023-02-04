import random
import string
from dateutil.relativedelta import relativedelta

from django.db.models.signals import pre_delete, post_save, pre_save
from django.dispatch import receiver

from home.models import Contrato, Imovei, Locatario, Usuario
from home.models import Parcela


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
        # Gera as parcelas quando o contrato é criado:
        for x in range(0, contrato.duracao):
            data_entrada = contrato.data_entrada
            data = data_entrada.replace(day=contrato.dia_vencimento) + relativedelta(months=x)

            codigos_existentes = list(
                Parcela.objects.filter(do_contrato=contrato.pk).values("codigo").values_list('codigo', flat=True))
            while True:
                recibo_codigo = ''.join(
                    random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in
                    range(6))
                if recibo_codigo not in codigos_existentes:
                    Parcela.objects.create(do_contrato=contrato, data_pagm_ref=data,
                                           codigo=f'{recibo_codigo[:3]}-{recibo_codigo[3:]}')
                    break
