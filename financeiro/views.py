from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Alugue_seu_imovel import settings
from financeiro.models import PacoteConfig
from financeiro.funcoes_proprias import loja_info


@login_required
def painel_loja(request):
    configs = PacoteConfig.objects.latest("data_registro")
    loja_info_ = loja_info(configs)

    context = {'SITE_NAME': settings.SITE_NAME, 'loja_info': loja_info_}
    return render(request, 'painel_loja.html', context)
