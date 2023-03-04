import random
import string
from dateutil.relativedelta import relativedelta

from django.db.models.signals import pre_delete, post_save, pre_save, post_delete
from django.dispatch import receiver

from home.models import Contrato, Imovei, Locatario, Parcela, Pagamento, Usuario

from notifications.signals import notify
from notifications.models import Notification


def gerenciar_parcelas(instance_contrato):
    # Editar as parcelas quando o contrato é editado:
    Parcela.objects.filter(do_contrato=instance_contrato.pk).delete()

    # RECRIA AS PARCELAS, MAS NÃO SERIA MELHOR MANTER RECIBOS TRUE PARA OS MESES QUE JÁ RECEBERAM RECIBO? NÃO PERCA O PROXIMO EPISODIO
    for x in range(0, instance_contrato.duracao):
        data_entrada = instance_contrato.data_entrada
        data = data_entrada.replace(day=instance_contrato.dia_vencimento) + relativedelta(months=x)

        codigos_existentes = list(
            Parcela.objects.filter(do_contrato=instance_contrato).values("codigo").values_list('codigo', flat=True))
        while True:
            recibo_codigo = ''.join(
                random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in
                range(6))
            if recibo_codigo not in codigos_existentes:
                parcela = Parcela(do_usuario=instance_contrato.do_locador, do_contrato=instance_contrato,
                                  do_imovel=instance_contrato.do_imovel, do_locatario=instance_contrato.do_locatario,
                                  data_pagm_ref=data, codigo=f'{recibo_codigo[:3]}-{recibo_codigo[3:]}')
                parcela.save()
                break

    # "Apagar" notificações de recibos que se referem a parcelas fora do novo período do
    # contrato(data de entrada-saída)
    notificacoes_user = Notification.objects.filter(recipient=instance_contrato.do_locador, deleted=False)
    parcelas_pks = Parcela.objects.filter(do_contrato=instance_contrato).values_list('pk', flat=True)
    for notificacao in notificacoes_user:
        if notificacao.target not in parcelas_pks:
            notificacao.delete()


def tratar_pagamentos(instance_contrato, delete=False):
    # Pegar informações para tratamento
    contrato = Contrato.objects.get(pk=instance_contrato.pk)
    parcelas = Parcela.objects.filter(do_contrato=contrato.pk).order_by('pk')

    # Recalcular as parcelas (model Parcela) pagas a partir do tt de pagamentos armazenados no seu respectivo contrato
    pagamentos_tt = int(contrato.pagamento_total())
    valor_mensal = int(contrato.valor_mensal)
    for mes_n, parcela in enumerate(parcelas):
        if pagamentos_tt > valor_mensal:
            # print(f'Mês {mes_n}: Mensalidade({valor_mensal}), pois o pagamentos_total({pagamentos_tt}) é maior')
            parcela.tt_pago = valor_mensal
            pagamentos_tt -= valor_mensal
        elif 0 < pagamentos_tt <= valor_mensal:
            # print(f'Mês {mes_n}: pagamentos_tt({pagamentos_tt}), pois é menor que a mensalidade({valor_mensal})')
            parcela.tt_pago = pagamentos_tt
            pagamentos_tt -= valor_mensal
            # parcela.recibo_entregue = False
        else:
            # print(f'Mês {mes_n}: 0, pois o pagamento total está em {pagamentos_tt}')
            parcela.tt_pago = 0
            # parcela.recibo_entregue = False
        parcela.save(update_fields=['tt_pago', 'recibo_entregue'])

    # Notificação
    # Listar actor_object_id de cada notificação do usuario
    if delete is False:
        notif_exist = Notification.objects.filter(recipient=parcelas[0].do_usuario).values_list('actor_object_id')
        lista_actor_object_id = []
        if notif_exist:
            for i in notif_exist:
                lista_actor_object_id.append(int(i[0]))

        # Enviar a notificação de recibo
        for parcela in parcelas:
            mensagem = f'O Pagamento de {parcela.do_contrato.do_locatario.primeiro_ultimo_nome()} referente à ' \
                       f'parcela de {parcela.data_pagm_ref.strftime("%B/%Y").upper()} do contrato ' \
                       f'{parcela.do_contrato.codigo} foi detectado. Confirme a entrega do recibo.'

            if parcela.tt_pago == valor_mensal and parcela.recibo_entregue is False and parcela.pk not in \
                    lista_actor_object_id:
                notify.send(sender=parcela, recipient=parcela.do_usuario, verb=f'Recibo',
                            description=mensagem)


@receiver(pre_save, sender=Usuario)
def usuario_save(sender, instance, **kwargs):
    if instance.id is None:  # if Criado
        pass
    else:
        # Apaga todos os recibos em pdf do usuario(para que novos possam ser criados) quando se modifica informações
        # desta model contidas neles
        ante = Usuario.objects.get(id=instance.pk)
        if ante.RG != instance.RG or ante.CPF != instance.CPF or ante.first_name != instance.first_name or \
                ante.last_name != instance.last_name:
            contratos = Contrato.objects.filter(do_locador=instance)
            for contrato in contratos:
                contrato.recibos_pdf.delete()


@receiver(pre_save, sender=Locatario)
def locatario_save(sender, instance, **kwargs):
    if instance.id is None:  # if Criado
        pass
    else:
        # Apaga todos os recibos em pdf do locatario(para que novos possam ser criados) quando se modifica
        # informações desta model contidas neles
        ante = Locatario.objects.get(id=instance.pk)
        if ante.RG != instance.RG or ante.CPF != instance.CPF or ante.nome != instance.nome:
            contratos = Contrato.objects.filter(do_locatario=instance)
            for contrato in contratos:
                contrato.recibos_pdf.delete()


@receiver(pre_save, sender=Contrato)
def contrato_save(sender, instance, **kwargs):
    if instance.id is None:  # if Criado
        pass
    else:
        # Após modificar um contrato(parametros: duracao e data_entrada):
        # Editar as parcelas quando o contrato é editado (função gerenciar_parcelas):
        # Recalc. as parcelas (model Parcela) pagas a partir do tt de pagamentos armazenados no seu respectivo contrato
        # Enviar as notificações relacionadas
        # com a função: tratar_pagamentos
        ante = Contrato.objects.get(id=instance.pk)
        if ante.duracao != instance.duracao or ante.data_entrada != instance.data_entrada:
            gerenciar_parcelas(instance_contrato=instance)
            tratar_pagamentos(instance_contrato=instance)


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


@receiver(post_delete, sender=Pagamento)
def pagamento_delete(sender, instance, **kwards):
    # Após apagar um pagamento:
    # Recalcular as parcelas (model Parcela) pagas a partir do tt de pagamentos armazenados no seu respectivo contrato
    # Enviar as notificações relacionadas
    # com a função: tratar_pagamentos
    tratar_pagamentos(instance_contrato=instance.ao_contrato, delete=True)

    # "Apagar" notificações de recibos que se referem a parcelas não kitadas (apenas ao deletar pagamentos)
    notificacoes_user = Notification.objects.filter(recipient=instance.ao_locador, deleted=False)
    parcelas_pks = Parcela.objects.filter(do_contrato=instance.ao_contrato,
                                          tt_pago__lt=instance.ao_contrato.valor_mensal).values_list('pk', flat=True)
    for notificacao in notificacoes_user:
        if notificacao.target not in parcelas_pks:
            notificacao.delete()


@receiver(post_save, sender=Pagamento)
def pagamento_update(sender, instance, created, **kwargs):
    # Após criar um pagamento:
    # Recalcular as parcelas (model Parcela) pagas a partir do tt de pagamentos armazenados no seu respectivo contrato
    # Enviar as notificações relacionadas
    # com a função: tratar_pagamentos
    tratar_pagamentos(instance_contrato=instance.ao_contrato)
