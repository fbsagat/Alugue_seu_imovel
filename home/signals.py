from django.db.models.signals import pre_delete, post_save, pre_init
from django.dispatch import receiver
from home.models import Contrato, Imovei, Locatario


# @receiver(pre_init, sender=Contrato)
# def verificar_vencimento(sender, args, **kwargs):
#     pass


@receiver(pre_delete, sender=Contrato)
def remover_do_imovel_delete(sender, instance, **kwards):
    contrato = Contrato.objects.get(pk=instance.pk)
    imovel = Imovei.objects.get(pk=contrato.do_imovel.pk)
    locatario = Locatario.objects.get(pk=contrato.do_locatario.pk)
    if imovel.com_locatario is True:
        locatario.com_imoveis.remove(imovel)
        locatario.com_contratos.remove(contrato)
        imovel.com_locatario = None
        imovel.contrato_atual = None
        imovel.save()
        locatario.save()


@receiver(post_save, sender=Contrato)
def remover_do_imovel_update(sender, instance, created, **kwargs):
    contrato = Contrato.objects.get(pk=instance.pk)
    imovel = Imovei.objects.get(pk=contrato.do_imovel.pk)
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


# pre_init.connect(remover_do_imovel_update)
# post_save.connect(remover_do_imovel_update, sender=Contrato)
# pre_delete.connect(remover_do_imovel_delete, sender=Contrato)
