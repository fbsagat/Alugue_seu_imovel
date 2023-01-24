from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from home.models import Contrato, Imovei, Locatario, Usuario
from home.funcoes_proprias import gerar_recibos
from num2words import num2words


@receiver(pre_delete, sender=Contrato)
def contrato_delete(sender, instance, **kwards):
    # Remove locador do imovel quando deleta um contrato
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
def contrato_update(sender, instance, created, **kwargs):
    # Remove locador do imovel quando um contrato fica inativo e adiciona quando fica ativo
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

    # Gera os recibos quando o contrato é criado ou modificado
    usuario = Usuario.objects.get(pk=contrato.do_locador.pk)

    reais = int(contrato.valor_mensal[:-2])
    centavos = int(contrato.valor_mensal[-2:])
    num_ptbr_reais = num2words(reais, lang='pt-br')
    completo = ''
    if centavos > 0:
        num_ptbr_centavos = num2words(centavos, lang='pt-br')
        completo = f' E {num_ptbr_centavos} centavos'

    dados = {'cod_recibo': ['465736', '463416', '125736', '465676', '465756', '465346', '474936'],
             'cod_contrato': '4536-3382',
             'nome_locador': f'{usuario.first_name.upper()} {usuario.last_name.upper()}',
             'rg_locd': '5667789',
             'cpf_locd': '005.234.342-10',
             'nome_locatario': f'{locatario.nome.upper()}',
             'rg_loct': f'{locatario.RG}',
             'cpf_loct': f'{locatario.CPF}',
             'valor_e_extenso': f'{contrato.valor_br()} ({num_ptbr_reais.upper()} REAIS{completo.upper()})',
             'mes_e_ano': ['NOVEMBRO', '2022', 'DEZEMBRO', '2022', 'JANEIRO', '2023', 'FEVEREIRO', '2023', 'MARÇO',
                           '2023', 'ABRIL', '2023', 'MAIO', '2023'],
             'endereco': f"{imovel.endereco}",
             'cidade': 'Belém',
             'data': '________________, ____ de _________ de ________'}

    gerar_recibos(dados=dados)
