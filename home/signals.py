import os, json, datetime
from dateutil.relativedelta import relativedelta

from Alugue_seu_imovel import settings

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import pre_delete, post_save, pre_save, post_delete
from django.db import transaction
from django.dispatch import receiver

from home.funcoes_proprias import gerar_contrato_pdf
from home.models import Contrato, Locatario, Parcela, Pagamento, Usuario, Tarefa, Anotacoe, Sugestao, Slot, Imovei, \
    ContratoModelo, modelo_variaveis, modelo_condicoes


# FUNÇÕES COMPARTILHADAS \/  ---------------------------------------
def gerenciar_parcelas(instance_contrato):
    # Criar as parcelas que não existem, definir apagadas as parcelas fora do range('data_pagm_ref')
    # e manter as que já existem e estão no range

    parcelas = Parcela.objects.filter(do_contrato=instance_contrato)
    parcelas_datas = parcelas.values_list('data_pagm_ref', flat=True)
    if parcelas:
        # Criar as novas parcelas dentro do range, manter as existentes(dentro tbm) e
        # 'definir apagadas' parcelas fora do range
        data_entrada = instance_contrato.data_entrada

        # Apagar parcelas fora do range:
        # Pegar datas atualizadas a partir da data de entrada e duração do contrato
        datas = []
        for x in range(0, instance_contrato.duracao):
            data = data_entrada.replace(day=instance_contrato.dia_vencimento) + relativedelta(months=x)
            datas.append(data)
        for parcela in parcelas:
            if parcela.data_pagm_ref not in datas:
                parcela.definir_apagada()
                if parcela.da_tarefa:
                    Tarefa.objects.filter(pk=parcela.da_tarefa.pk).update(apagada=True)
            else:
                parcela.restaurar()
                if parcela.da_tarefa:
                    Tarefa.objects.filter(pk=parcela.da_tarefa.pk).update(apagada=False)

        for data in datas:
            if data not in parcelas_datas:
                parcela = Parcela(do_usuario=instance_contrato.do_locador, do_contrato=instance_contrato,
                                  do_imovel=instance_contrato.do_imovel,
                                  do_locatario=instance_contrato.do_locatario,
                                  data_pagm_ref=data)
                parcela.save()
    else:
        # Criar parcelas zeradas
        for x in range(0, instance_contrato.duracao):
            data_entrada = instance_contrato.data_entrada
            data = data_entrada.replace(day=instance_contrato.dia_vencimento) + relativedelta(months=x)
            parcela = Parcela(do_usuario=instance_contrato.do_locador, do_contrato=instance_contrato,
                              do_imovel=instance_contrato.do_imovel,
                              do_locatario=instance_contrato.do_locatario,
                              data_pagm_ref=data)
            parcela.save()


def tratar_pagamentos(instance_contrato):
    # Pegar informações para tratamento
    contrato = Contrato.objects.get(pk=instance_contrato.pk)
    parcelas = Parcela.objects.filter(do_contrato=contrato.pk, apagada=False).order_by('data_pagm_ref')

    # Pega o total pago para este contrato e distribui para as parcelas do contrato
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
        parcela.save(update_fields=['tt_pago'])


def criar_uma_tarefa(usuario, tipo_conteudo, objeto_id, lida=False):
    # Caso exista: Tenta recuperar apagada, desfazer lida, etc...
    # cada ContentType tem sua regra, personalizar abaixo \/
    try:
        tarefa = Tarefa.objects.get(autor_classe=tipo_conteudo, objeto_id=objeto_id)
        if tarefa.autor_classe == ContentType.objects.get_for_model(Parcela):
            if tarefa.content_object.apagada is False:
                tarefa.restaurar()
        elif tarefa.autor_classe == ContentType.objects.get_for_model(Anotacoe):
            tarefa.restaurar()
        elif tarefa.autor_classe == ContentType.objects.get_for_model(Sugestao):
            tarefa.restaurar()
        elif tarefa.autor_classe == ContentType.objects.get_for_model(Slot):
            tarefa.definir_nao_lida()
        return tarefa
    except:
        # Caso não exista, criar a tarefa requisitada para o objeto
        tarefa = Tarefa()
        tarefa.do_usuario = usuario
        tarefa.autor_classe = tipo_conteudo
        tarefa.objeto_id = objeto_id
        tarefa.lida = lida
        tarefa.save()
        return tarefa


# Gerenciadores de pre_save \/  ---------------------------------------
@receiver(pre_save, sender=Parcela)
def parcela_pre_save(sender, instance, **kwargs):
    if instance.pk is None:  # if criado
        pass
    else:
        # Parcela quitada? então criar uma tarefa para este objeto e atribuí-la à parcela
        tipo_conteudo = ContentType.objects.get_for_model(Parcela)
        objeto_id = instance.pk
        if instance.esta_pago():
            usuario = instance.do_contrato.do_locador
            tarefa = criar_uma_tarefa(usuario=usuario, tipo_conteudo=tipo_conteudo, objeto_id=objeto_id, lida=True)
            Parcela.objects.filter(pk=instance.pk).update(da_tarefa=tarefa)
        else:
            try:
                tarefa = Tarefa.objects.get(autor_classe=tipo_conteudo, objeto_id=objeto_id)
                tarefa.definir_apagada()
            except:
                pass
        if instance.recibo_entregue:
            try:
                Tarefa.objects.filter(pk=instance.da_tarefa.pk).update(data_lida=datetime.datetime.now())
            except:
                pass


@receiver(pre_save, sender=Usuario)
def usuario_pre_save(sender, instance, **kwargs):
    if instance.pk is None:  # if criado
        pass
    else:
        # Apaga todos os recibos em pdf do usuário(para que novos possam ser criados) quando se modifica informações
        # desta model contidas neles (RG, CPF, First Name, Last Name)
        # Também apaga quando o usuário troca o preenchimento do campo data
        ante = Usuario.objects.get(pk=instance.pk)

        try:
            if ante.RG != instance.RG or ante.cpf() != instance.cpf() or ante.first_name != instance.first_name \
                    or ante.last_name != instance.last_name \
                    or ante.recibo_preenchimento != int(instance.recibo_preenchimento):
                contratos = Contrato.objects.filter(do_locador=instance)
                for contrato in contratos:
                    contrato.recibos_pdf.delete()
        except:
            pass


@receiver(pre_save, sender=Locatario)
def locatario_pre_save(sender, instance, **kwargs):
    if instance.pk is None or kwargs['raw']:  # Se criado ou vem de fixture
        pass
    else:
        # Apaga todos os recibos em pdf do locatário(para que novos possam ser criados) quando se modifica
        # informações desta model contidas neles
        ante = Locatario.objects.get(pk=instance.pk)
        if ante.RG != instance.RG or ante.cpf() != instance.cpf() or ante.nome != instance.nome:
            contratos = Contrato.objects.filter(do_locatario=instance)
            for contrato in contratos:
                contrato.recibos_pdf.delete()
            pass


@receiver(pre_save, sender=Contrato)
def contrato_pre_save(sender, instance, **kwargs):
    if instance.pk is None or kwargs['raw']:  # Se criado ou vem de fixture
        pass
    else:
        # Após modificar/editar um contrato(parameters: duracao e data_entrada):
        # Editar as parcelas (função gerenciar_parcelas)
        # E com a função: tratar_pagamentos \/
        #   1. Recalcular as parcelas (model Parcela) pagas a partir do total de pagamentos armazenados
        #   no seu respectivo contrato.
        #   2. Enviar as tarefas relacionadas.

        ante = Contrato.objects.get(pk=instance.pk)
        if ante.duracao != instance.duracao or ante.data_entrada != instance.data_entrada:
            gerenciar_parcelas(instance_contrato=instance)
            tratar_pagamentos(instance_contrato=instance)

        if instance.em_posse:
            Tarefa.objects.filter(pk=instance.da_tarefa.pk).update(data_lida=datetime.datetime.now())


@receiver(pre_save, sender=Anotacoe)
def anotacao_pre_save(sender, instance, **kwargs):
    # Criar e apagar tarefa referente a anotações
    if instance.pk is None or kwargs['raw']:  # Se criado ou vem de fixture
        pass
    else:
        # If editado
        ante = Anotacoe.objects.get(pk=instance.pk)
        if instance.tarefa is False and ante.tarefa != instance.tarefa:
            # Defini apagada a tarefa referente à anotação se o usuário ao editar a anotação, desmarcar o botão tarefa.
            tarefa = Tarefa.objects.filter(autor_classe=ContentType.objects.get_for_model(Anotacoe),
                                           objeto_id=instance.pk).first()
            if tarefa:
                tarefa.definir_apagada()

        elif instance.tarefa is True and ante.tarefa != instance.tarefa:
            # Criar a tarefa referente à anotação se o usuário ao editar a anotação, marcar o botão tarefa.
            usuario = ante.do_usuario
            tipo_conteudo = ContentType.objects.get_for_model(Anotacoe)
            objeto_id = instance.pk
            criar_uma_tarefa(usuario=usuario, tipo_conteudo=tipo_conteudo, objeto_id=objeto_id)
        if instance.feito:
            try:
                Tarefa.objects.filter(pk=instance.da_tarefa.pk).update(data_lida=datetime.datetime.now())
            except:
                pass


@receiver(pre_save, sender=Sugestao)
def sugestao_pre_save(sender, instance, **kwargs):
    if instance.pk is None:  # if criado
        pass
    else:
        if instance.aprovada is True:
            usuario = instance.do_usuario
            tipo_conteudo = ContentType.objects.get_for_model(Sugestao)
            objeto_id = instance.pk
            tarefa = criar_uma_tarefa(usuario=usuario, tipo_conteudo=tipo_conteudo, objeto_id=objeto_id)
            Sugestao.objects.filter(pk=instance.pk).update(da_tarefa=tarefa)
        else:
            if instance.da_tarefa:
                instance.da_tarefa.definir_apagada()


# Gerenciadores de post_save \/  ---------------------------------------
@receiver(post_save, sender=ContratoModelo)
def contrato_modelo_post_save(sender, instance, created, **kwargs):
    # Tem outro gerar_contrato_pdf em visualizar_modelo em views (backup deste)
    if instance.verificar_utilizacao_config() and not instance.verificar_utilizacao_usuarios():
        pass
    else:
        dados = {'modelo_pk': instance.pk, 'modelo': instance, 'usuario_username': str(instance.autor.username),
                 'contrato_modelo_code': instance.autor.contrato_modelo_code()}
        link = gerar_contrato_pdf(dados=dados, visualizar=True)
        variaveis = []
        for i, j in modelo_variaveis.items():
            if j[0] in instance.corpo:
                variaveis.append(i)
        variaveis = list(dict.fromkeys(variaveis))
        condicoes = []
        for i, j in modelo_condicoes.items():
            if j[0] in instance.corpo:
                condicoes.append(i)
        condicoes = list(dict.fromkeys(condicoes))
        ContratoModelo.objects.filter(pk=instance.pk).update(variaveis=variaveis, condicoes=condicoes, visualizar=link)


@receiver(post_save, sender=Usuario)
def usuario_post_save(sender, instance, created, **kwargs):
    if created:
        for _ in range(0, 3):
            Slot.objects.create(do_usuario=instance, gratuito=True)


@receiver(post_save, sender=Anotacoe)
def anotacao_post_save(sender, instance, **kwargs):
    # Criar e apagar tarefa referente a anotações
    if instance.tarefa:
        usuario = instance.do_usuario
        tipo_conteudo = ContentType.objects.get_for_model(Anotacoe)
        objeto_id = instance.pk
        tarefa = criar_uma_tarefa(usuario=usuario, tipo_conteudo=tipo_conteudo, objeto_id=objeto_id,
                                  lida=True if instance.feito else False)
        Anotacoe.objects.filter(pk=instance.pk).update(da_tarefa=tarefa)


@transaction.atomic
@receiver(post_save, sender=Locatario)
def locatario_post_save(sender, instance, **kwargs):
    if instance.temporario is True:
        tipo_conteudo = ContentType.objects.get_for_model(Locatario)
        tarefa = criar_uma_tarefa(usuario=instance.do_locador, tipo_conteudo=tipo_conteudo, objeto_id=instance.pk)
        instance.da_tarefa = tarefa
        Locatario.objects.filter(pk=instance.pk).update(da_tarefa=tarefa)


@transaction.atomic
@receiver(post_save, sender=Contrato)
def contrato_post_save(sender, instance, created, **kwargs):
    lida = True if instance.em_posse else False
    # Pega os dados para tratamento:
    if created:
        # Gera as parcelas quando o contrato é criado:
        gerenciar_parcelas(instance)
        # Criar tarefa 'contrato criado' com o botão 'receber contrato'
        tipo_conteudo = ContentType.objects.get_for_model(Contrato)
        tarefa = criar_uma_tarefa(usuario=instance.do_locador, tipo_conteudo=tipo_conteudo, objeto_id=instance.pk,
                                  lida=lida)
        Contrato.objects.filter(pk=instance.pk).update(da_tarefa=tarefa)


@receiver(post_save, sender=Pagamento)
def pagamento_post_save(sender, instance, created, **kwargs):
    # Após criar um pagamento:
    # Com a função: tratar_pagamentos \/
    # 1. Recalcular as parcelas (model Parcela) pagas a partir do total de pagamentos armazenados
    # no seu respectivo contrato
    # 2. Enviar as tarefas relacionadas
    tratar_pagamentos(instance_contrato=instance.ao_contrato)


# Gerenciadores de pre_delete \/  ---------------------------------------
@transaction.atomic
@receiver(pre_delete, sender=Contrato)
def contrato_pre_delete(sender, instance, **kwards):
    # Apagar a tarefa desta anotação
    if instance.da_tarefa:
        instance.da_tarefa.delete()


# Apaga as tarefas dos objetos quando eles forem apagados \/
@receiver(pre_delete, sender=Anotacoe)
def anotacao_pre_delete(sender, instance, **kwargs):
    # Apagar a tarefa desta anotação
    if instance.da_tarefa:
        Tarefa.objects.filter(pk=instance.da_tarefa.pk).delete()


@receiver(pre_delete, sender=Sugestao)
def sugestao_pre_delete(sender, instance, **kwargs):
    # Apagar a tarefa desta anotação
    if instance.da_tarefa:
        Tarefa.objects.filter(pk=instance.da_tarefa.pk).delete()


@receiver(pre_delete, sender=Locatario)
def locatario_pre_delete(sender, instance, **kwargs):
    # Apagar a tarefa deste locatário
    if instance.da_tarefa:
        Tarefa.objects.filter(pk=instance.da_tarefa.pk).delete()


@receiver(pre_delete, sender=Parcela)
def parcela_pre_delete(sender, instance, **kwargs):
    # Apagar a tarefa desta parcela
    if instance.da_tarefa:
        Tarefa.objects.filter(pk=instance.da_tarefa.pk).delete()


@receiver(pre_delete, sender=Slot)
def slot_pre_delete(sender, instance, **kwargs):
    # Apagar a tarefa desta parcela
    if instance.da_tarefa:
        Tarefa.objects.filter(pk=instance.da_tarefa.pk).delete()


# Gerenciadores de post_delete \/  ---------------------------------------
@receiver(post_delete, sender=Pagamento)
def pagamento_post_delete(sender, instance, **kwards):
    # Após apagar um pagamento:
    # Com a função: tratar_pagamentos \/
    # 1. Recalcular as parcelas (model Parcela) pagas a partir do total de pagamentos armazenados
    # no seu respectivo contrato
    # 2. Enviar as tarefas relacionadas
    tratar_pagamentos(instance_contrato=instance.ao_contrato)


# Gerenciadores de login e logout \/  ---------------------------------------
@receiver(user_logged_in)
def usuario_fez_login(sender, user, **kwargs):
    if user.is_superuser and user.username == 'fbaugusto':
        caminho = fr"C:\Users\Fabio\PycharmProjects\Alugue_seu_imovel\home\fixtures\recibos_entregues.json"
        caminho_2 = fr"C:\Users\Fabio\PycharmProjects\Alugue_seu_imovel\home\fixtures\dados_do_predio.json"
        caminho_3 = fr"C:\Users\Fabio\PycharmProjects\Alugue_seu_imovel\home\fixtures\locatarios_cpfs.json"

        # Marcar os recibos entregues
        if os.path.isfile(caminho):
            arquivo = open(caminho)
            dados = json.load(arquivo)
            for key, value in dados['dados'].items():
                parcelas = Parcela.objects.filter(do_contrato=key).order_by('data_pagm_ref')
                for index, parcela in enumerate(parcelas):
                    parcela.recibo_entregue = 1 if index < value else 0
                    parcela.save(update_fields=['recibo_entregue', ])
                    if parcela.da_tarefa:
                        parcela.da_tarefa.lida_e_data() if index < value else 0
            arquivo.close()
            os.remove(caminho)

        if os.path.isfile(caminho_2):
            os.remove(caminho_2)

        # Preencher os CPFs criptografados dos locatários
        if os.path.isfile(caminho_3):
            arquivo = open(caminho_3)
            dados = json.load(arquivo)
            for n, cpf in enumerate(dados):
                locatario = Locatario.objects.get(pk=n + 1)
                cpf_enc = bytes(cpf, 'UTF-8')
                locatario.cript_cpf = cpf_enc
                locatario.save(update_fields=['cript_cpf', ])
                arquivo.close()
            os.remove(caminho_3)

            # Criar slots restantes
            imoveis_qtd = Imovei.objects.filter(do_locador=user).count()
            if imoveis_qtd > 3:
                for n in range(3, imoveis_qtd):
                    Slot.objects.create(do_usuario=user, gratuito=False, tickets=1)

    # Verificar se tem algum slot vencido e enviar uma notificação avisando o usuário, caso a notificação já exista,
    # não enviar nada.
    inativos_com_imovel = Slot.objects.inativos_com_imovel().filter(do_usuario=user)
    for slot in inativos_com_imovel:
        tipo_conteudo = ContentType.objects.get_for_model(Slot)
        tarefa = criar_uma_tarefa(usuario=user, tipo_conteudo=tipo_conteudo, objeto_id=slot.pk)
        Slot.objects.filter(pk=slot.pk).update(da_tarefa=tarefa)


@receiver(user_logged_out)
def usuario_fez_logout(sender, user, **kwargs):
    # Apagar arquivos temporários da sessão do usuário
    # 1. Tabela_docs
    diretorio = rf'{settings.MEDIA_ROOT}/tabela_docs'
    se_existe = os.path.exists(diretorio)
    if not se_existe:
        os.makedirs(diretorio)
    for file in os.listdir(diretorio):
        if file.endswith(f"{user}.pdf"):
            os.remove(os.path.join(diretorio, file))

    # 2. Contrato_docs
    diretorio = f'{settings.MEDIA_ROOT}/contrato_docs'
    se_existe = os.path.exists(diretorio)
    if not se_existe:
        os.makedirs(diretorio)
    code = user.contrato_code()
    for file in os.listdir(diretorio):
        if file.startswith(code):
            os.remove(os.path.join(diretorio, file))
