import os
import random
import string
from dateutil.relativedelta import relativedelta

from Alugue_seu_imovel import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import pre_delete, post_save, pre_save, post_delete
from django.dispatch import receiver

from home.models import Contrato, Imovei, Locatario, Parcela, Pagamento, Usuario, Tarefa


def gerenciar_parcelas(instance_contrato):
    # Fazer algumas coisas se tiver parcelas anteriormente(acontece qdo o usuario modifica o período do contrato)
    parcelas_anter = Parcela.objects.filter(do_contrato=instance_contrato).values()[:]

    if parcelas_anter:
        Parcela.objects.filter(do_contrato=instance_contrato.pk).delete()

    # Criar as parcelas (acontece sempre (contrato criado e editado)):
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

    if parcelas_anter:
        # No ato de editar o período do contrato essa função irá copiar o dado(codigo)
        # das parcelas antigas(apagadas) que possuem a mesma data para as novas parcelas.
        parcelas_novas = Parcela.objects.filter(do_contrato=instance_contrato)

        datas_do_anterior_trat = []
        for i in parcelas_anter:
            datas_do_anterior_trat.append(str(i['data_pagm_ref']))

        for parcela in parcelas_novas:
            if str(parcela.data_pagm_ref) in datas_do_anterior_trat:
                index = datas_do_anterior_trat.index(str(parcela.data_pagm_ref))
                parcela.codigo = parcelas_anter[index]['codigo']
                parcela.save(update_fields=['codigo'])

        # "Apagar" tarefas antigas deste contrato
        tarefas_user = Tarefa.objects.filter(do_usuario=instance_contrato.do_locador, deleted=False)
        parcelas_pks = Parcela.objects.filter(do_contrato=instance_contrato).values_list('pk', flat=True)
        for tarefa in tarefas_user:
            if tarefa.autor_id not in parcelas_pks:
                tarefa.delete()


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
    # Listar autor_id de cada notificação do usuario
    if delete is False:
        tarefa_exist = Tarefa.objects.filter(do_usuario=parcelas[0].do_usuario).values_list('autor_id')
        lista_autor_id = []
        if tarefa_exist:
            for i in tarefa_exist:
                lista_autor_id.append(int(i[0]))

        # Enviar a notificação de recibo
        for parcela in parcelas:
            mensagem = f'O Pagamento de {parcela.do_contrato.do_locatario.primeiro_ultimo_nome()} referente à ' \
                       f'parcela de {parcela.data_pagm_ref.strftime("%B/%Y").upper()} do contrato ' \
                       f'{parcela.do_contrato.codigo} foi detectado. Confirme a entrega do recibo.'

            if parcela.tt_pago == valor_mensal and parcela.pk not in lista_autor_id:
                tarefa = Tarefa()
                tarefa.autor_id = parcela.pk
                tarefa.do_usuario = parcela.do_usuario
                tarefa.autor_tipo = 1
                tarefa.texto = mensagem
                tarefa.dados = {'recibo_entregue': parcela.recibo_entregue}
                tarefa.save()


@receiver(user_logged_in)
def usuario_fez_login(sender, user, **kwargs):
    pass


@receiver(user_logged_out)
def usuario_fez_logout(sender, user, **kwargs):
    file = rf'{settings.MEDIA_ROOT}/tabela_docs/tabela_{user.uuid}_{user}.pdf'
    if os.path.exists(file):
        os.remove(file)


@receiver(pre_save, sender=Usuario)
def usuario_save(sender, instance, **kwargs):
    if instance.pk is None:  # if Criado
        pass
    else:
        # Apaga todos os recibos em pdf do usuario(para que novos possam ser criados) quando se modifica informações
        # desta model contidas neles
        ante = Usuario.objects.get(pk=instance.pk)
        if ante.RG != instance.RG or ante.CPF != instance.CPF or ante.first_name != instance.first_name or \
                ante.last_name != instance.last_name or ante.recibo_preenchimento != instance.recibo_preenchimento:
            contratos = Contrato.objects.filter(do_locador=instance)
            for contrato in contratos:
                contrato.recibos_pdf.delete()


@receiver(pre_save, sender=Locatario)
def locatario_save(sender, instance, **kwargs):
    if instance.pk is None:  # if Criado
        pass
    else:
        # Apaga todos os recibos em pdf do locatario(para que novos possam ser criados) quando se modifica
        # informações desta model contidas neles
        ante = Locatario.objects.get(pk=instance.pk)
        if ante.RG != instance.RG or ante.CPF != instance.CPF or ante.nome != instance.nome:
            contratos = Contrato.objects.filter(do_locatario=instance)
            for contrato in contratos:
                contrato.recibos_pdf.delete()


@receiver(pre_save, sender=Contrato)
def contrato_save(sender, instance, **kwargs):
    if instance.pk is None:  # if Criado
        pass
    else:
        # Após modificar um contrato(parametros: duracao e data_entrada):
        # Editar as parcelas quando o contrato é editado (função gerenciar_parcelas):
        # Recalc. as parcelas (model Parcela) pagas a partir do tt de pagamentos armazenados no seu respectivo contrato
        # Enviar as notificações relacionadas
        # com a função: tratar_pagamentos
        ante = Contrato.objects.get(pk=instance.pk)
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
        gerenciar_parcelas(contrato)


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
    tarefa_user = Tarefa.objects.filter(do_usuario=instance.ao_locador)
    parcelas_pks = Parcela.objects.filter(do_contrato=instance.ao_contrato,
                                          tt_pago__lt=instance.ao_contrato.valor_mensal).values_list('pk', flat=True)
    for tarefa in tarefa_user:
        if tarefa.autor_id not in parcelas_pks:
            tarefa.delete()


@receiver(post_save, sender=Pagamento)
def pagamento_update(sender, instance, created, **kwargs):
    # Após criar um pagamento:
    # Recalcular as parcelas (model Parcela) pagas a partir do tt de pagamentos armazenados no seu respectivo contrato
    # Enviar as notificações relacionadas
    # com a função: tratar_pagamentos
    tratar_pagamentos(instance_contrato=instance.ao_contrato)
