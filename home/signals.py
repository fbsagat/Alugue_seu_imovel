import random
import string
from dateutil.relativedelta import relativedelta

from django.db.models.signals import pre_delete, post_save, pre_save, post_delete
from django.dispatch import receiver

from home.models import Contrato, Imovei, Locatario, Usuario
from home.models import Parcela, Pagamento


def distribuir_pagamentos(instance):
    contrato = Contrato.objects.get(pk=instance.ao_contrato.pk)
    parcelas = Parcela.objects.filter(do_contrato=contrato.pk).order_by('pk')

    total = int(contrato.pagamento_total())
    print(total)
    dividir = contrato.duracao
    limite = int(contrato.valor_mensal)

    for mes in range(0, dividir):
        x = limite if (total / (mes + 1)) >= limite else (total - (mes * limite))
        print(x)
        if x <= 0:
            parcela = parcelas[mes]
            parcela.tt_pago = 0
            parcela.save(update_fields=['tt_pago'])
            print(f'debug: {x} no mês {mes}, limite por mês é {limite}')
            break
        else:
            parcela = parcelas[mes]
            parcela.tt_pago = x
            parcela.save(update_fields=['tt_pago'])
            print(f'debug: {x} no mês {mes}, limite por mês é {limite}')


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
                    Parcela.objects.create(do_usuario=contrato.do_locador, do_contrato=contrato, do_imovel=imovel,
                                           do_locatario=locatario, data_pagm_ref=data,
                                           codigo=f'{recibo_codigo[:3]}-{recibo_codigo[3:]}')
                    break


@receiver(post_delete, sender=Pagamento)
def pagamento_delete(sender, instance, **kwards):
    # Após apagar um pagamento, recalcular as parcelas (model Parcela) pagas a partir do total de pagamentos armazenados
    # no seu respectivo contrato (função: pagamento_total)
    distribuir_pagamentos(instance=instance)


@receiver(post_save, sender=Pagamento)
def pagamento_update(sender, instance, created, **kwargs):
    # Após criar um pagamento, recalcular as parcelas (model Parcela) pagas a partir do total de pagamentos armazenados
    # no seu respectivo contrato (função: pagamento_total)
    distribuir_pagamentos(instance=instance)
