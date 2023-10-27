from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Alugue_seu_imovel import settings
from financeiro.models import PacoteConfig
from django.shortcuts import redirect, reverse


@login_required
def painel_loja(request):
    configs = PacoteConfig.objects.latest("data_registro")

    pub_key = settings.STRIPE_PUBLIC_KEY
    context = {'SITE_NAME': settings.SITE_NAME, 'loja_info': configs.loja_info(), 'pub_key': pub_key}
    return render(request, 'painel_loja.html', context)


@login_required
def pagar_pacote(request, pacote_index, forma):
    # validar estas entradas depois: pacote_index, forma
    configs = PacoteConfig.objects.latest("data_registro")

    valor = 0
    if forma == 'brl':
        valor = configs.loja_info()[int(pacote_index)]['valor_pct_brl']
    elif forma == 'btc':
        valor = configs.loja_info()[int(pacote_index)]['valor_pct_btc']

    return redirect(reverse('home:Painel Loja'))
