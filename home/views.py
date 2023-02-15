import locale
from num2words import num2words
from datetime import datetime
from os import path
from dateutil.relativedelta import relativedelta

from Alugue_seu_imovel import settings

from django.core.files import File
from django.views.generic import CreateView, DeleteView, FormView, UpdateView, ListView, TemplateView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render, reverse, get_object_or_404, Http404
from django.utils import timezone, dateformat
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import messages
from django.db.models.aggregates import Count, Sum

from home.new_context import forms_da_navbar
from home.funcoes_proprias import valor_format, gerar_recibos, gerar_tabela
from home.fakes_test import locatarios_ficticios, imoveis_ficticios, imov_grupo_fict, contratos_ficticios, \
    pagamentos_ficticios, gastos_ficticios, anotacoes_ficticias, usuarios_ficticios
from home.forms import FormCriarConta, FormHomePage, FormMensagem, FormEventos, FormAdmin, FormPagamento, FormGasto, \
    FormLocatario, FormImovel, FormAnotacoes, FormContrato, FormimovelGrupo, FormRecibos

from home.models import Locatario, Contrato, Pagamento, Gasto, Anotacoe, ImovGrupo, Usuario, Imovei, Parcela

locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')

# -=-=-=-=-=-=-=-= BOTÃO DASHBOARD -=-=-=-=-=-=-=-=

class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = 'exibir_dashboard.html'
    model = Locatario

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(Dashboard, self).get_context_data(**kwargs)
        context['SITE_NAME'] = settings.SITE_NAME
        return context


# -=-=-=-=-=-=-=-= BOTÃO EVENTOS -=-=-=-=-=-=-=-=


@login_required
def eventos(request, pk):
    user = Usuario.objects.get(pk=request.user.pk)
    form = FormEventos()
    pagamentos = gastos = locatarios = contratos = imoveis = anotacoes = pg_tt = gasto_tt = contr_tt = pag_m_gast = ''
    agreg_1 = agreg_2 = int()
    pesquisa_req = True if user.data_eventos_i and user.itens_eventos and user.qtd_eventos and user.ordem_eventos else \
        False

    data_eventos_i = user.data_eventos_i
    data_eventos_f = datetime.now()
    itens_eventos = user.itens_eventos
    qtd_eventos = user.qtd_eventos
    ordem_eventos = int(user.ordem_eventos)
    if ordem_eventos == 2:
        ordem = ''
    elif ordem_eventos == 1:
        ordem = '-'

    if pesquisa_req:
        form = FormEventos(initial={'qtd': user.qtd_eventos, 'data_eventos_i': user.data_eventos_i.strftime('%Y-%m-%d'),
                                    'itens_eventos': list(user.itens_eventos), 'ordem_eventos': user.ordem_eventos})
    if request.method == 'POST':
        form = FormEventos(request.POST)
        if form.is_valid():
            user.data_eventos_i = form.cleaned_data['data_eventos_i']
            user.itens_eventos = form.cleaned_data['itens_eventos']
            user.qtd_eventos = form.cleaned_data['qtd']
            user.ordem_eventos = form.cleaned_data['ordem_eventos']
            user.save(update_fields=["data_eventos_i", "itens_eventos", "qtd_eventos", "ordem_eventos"])

            data_eventos_i = form.cleaned_data['data_eventos_i']
            data_eventos_f = datetime.combine(form.cleaned_data['data_eventos_f'], datetime.now().time())
            itens_eventos = form.cleaned_data['itens_eventos']
            qtd_eventos = form.cleaned_data['qtd']
            ordem_eventos = int(form.cleaned_data['ordem_eventos'])
            if ordem_eventos == 2:
                ordem = ''
            elif ordem_eventos == 1:
                ordem = '-'

    if '1' in itens_eventos and pesquisa_req:
        pagamentos = Pagamento.objects.filter(ao_locador=request.user,
                                              data_pagamento__range=[data_eventos_i, data_eventos_f]).order_by(
            f'{ordem}data_pagamento')[:qtd_eventos]
        agreg_1 = pagamentos.aggregate(total=Sum("valor_pago"))
        if agreg_1["total"]:
            pg_tt = f'{valor_format(str(agreg_1["total"]))}'

    if '2' in itens_eventos and pesquisa_req:
        gastos = Gasto.objects.filter(do_locador=request.user, data__range=[data_eventos_i, data_eventos_f]).order_by(
            f'{ordem}data')[:qtd_eventos]
        agreg_2 = gastos.aggregate(total=Sum("valor"))
        if agreg_2["total"]:
            gasto_tt = f'{valor_format(str(agreg_2["total"]))}'

    if '1' and '2' in itens_eventos and pesquisa_req and agreg_1["total"] and agreg_2["total"]:
        pag_m_gast = valor_format(str(agreg_1["total"] - agreg_2["total"]))

    if '3' in itens_eventos and pesquisa_req:
        locatarios = Locatario.objects.filter(do_locador=request.user,
                                              data_registro__range=[data_eventos_i, data_eventos_f]).order_by(
            f'{ordem}data_registro')[:qtd_eventos]
    if '4' in itens_eventos and pesquisa_req:
        contratos = Contrato.objects.filter(do_locador=request.user,
                                            data_registro__range=[data_eventos_i, data_eventos_f]).order_by(
            f'{ordem}data_registro')[:qtd_eventos]
        contratotal = contratos.aggregate(total=Sum("valor_mensal"))["total"]
        if contratotal:
            contr_tt = f'{valor_format(str(contratotal))}'

    if '5' in itens_eventos and pesquisa_req:
        imoveis = Imovei.objects.filter(do_locador=request.user,
                                        data_registro__range=[data_eventos_i, data_eventos_f]).order_by(
            f'{ordem}data_registro')[:qtd_eventos]
    if '6' in itens_eventos and pesquisa_req:
        anotacoes = Anotacoe.objects.filter(do_usuario=request.user,
                                            data_registro__range=[data_eventos_i, data_eventos_f]).order_by(
            f'{ordem}data_registro')[:qtd_eventos]

    context = {'form': form, 'pagamentos': pagamentos, 'gastos': gastos, 'locatarios': locatarios,
               'contratos': contratos, 'imoveis': imoveis, 'anotacoes': anotacoes, 'pg_tt': pg_tt, 'gasto_tt': gasto_tt,
               'contr_tt': contr_tt, 'pag_m_gast': pag_m_gast, 'SITE_NAME': settings.SITE_NAME}

    return render(request, 'exibir_eventos.html', context)


# -=-=-=-=-=-=-=-= BOTÃO ATIVOS -=-=-=-=-=-=-=-=

class Perfil1(LoginRequiredMixin, ListView):
    template_name = 'exibir_ativos.html'
    model = Imovei
    context_object_name = 'imoveis'
    paginate_by = 12

    def get_queryset(self):
        self.object_list = Imovei.objects.ocupados().filter(do_locador=self.request.user).order_by('-data_registro')
        return self.object_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(Perfil1, self).get_context_data(**kwargs)
        context['imoveis_qtd'] = Imovei.objects.ocupados().filter(do_locador=self.request.user).count()
        context['SITE_NAME'] = settings.SITE_NAME
        return context


class Perfil2(LoginRequiredMixin, ListView):
    template_name = 'exibir_ativos.html'
    model = Locatario
    context_object_name = 'locatarios'
    paginate_by = 9

    def get_queryset(self):
        self.object_list = Locatario.objects.com_imoveis().filter(do_locador=self.request.user).order_by(
            '-data_registro')
        return self.object_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(Perfil2, self).get_context_data(**kwargs)
        context['locatario_qtd'] = Locatario.objects.com_imoveis().filter(do_locador=self.request.user).count()
        context['SITE_NAME'] = settings.SITE_NAME
        return context


class Perfil3(LoginRequiredMixin, ListView):
    template_name = 'exibir_ativos.html'
    model = Contrato
    context_object_name = 'contratos'
    paginate_by = 12

    def get_queryset(self):
        self.object_list = Contrato.objects.ativos().filter(do_locador=self.request.user).order_by('-data_registro')
        return self.object_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(Perfil3, self).get_context_data(**kwargs)
        context['contrato_qtd'] = Contrato.objects.filter(do_locador=self.request.user).count()
        context['SITE_NAME'] = settings.SITE_NAME
        return context


# -=-=-=-=-=-=-=-= BOTÃO REGISTRAR -=-=-=-=-=-=-=-=

# PAGAMENTO ---------------------------------------
@login_required
def registrar_pagamento(request):
    form = FormPagamento(request.user, request.POST)
    if form.is_valid():
        pagamento = form.save(commit=False)
        pagamento.ao_locador = request.user
        contrato_pk = request.POST.get('ao_contrato')
        locatario = Contrato.objects.get(pk=contrato_pk).do_locatario
        pagamento.do_locatario = locatario
        pagamento.save()
        messages.success(request, f"Pagamento registrado com sucesso!")
        if 'form1' in request.session:
            del request.session['form1']
        return redirect(request.META['HTTP_REFERER'])
    else:
        request.session['form1'] = request.POST
        messages.error(request, f"Formulário inválido!")
        return redirect(request.META['HTTP_REFERER'])


@login_required
def entregar_recibo(request, pk):
    pagamento = Pagamento.objects.get(pk=pk)
    if pagamento.ao_locador == request.user:
        if pagamento.recibo is True:
            pagamento.recibo = False
            pagamento.save()
            return redirect(request.META['HTTP_REFERER'])
        else:
            pagamento.data_de_recibo = timezone.now()
            data = dateformat.format(timezone.now(), 'd-m-Y')
            hora = dateformat.format(timezone.now(), 'H:i')
            pagamento.recibo = True
            pagamento.save()
            messages.warning(request, f"O recibo foi entregue! Resgistro criado em {data} às {hora}")
        return redirect(request.META['HTTP_REFERER'])
    else:
        return Http404


class ExcluirPagm(LoginRequiredMixin, DeleteView):
    model = Pagamento
    template_name = 'excluir_item.html'

    def get_success_url(self):
        return reverse_lazy('home:Pagamentos', args=[self.request.user.id])

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Pagamento, pk=self.kwargs['pk'], ao_locador=self.request.user)
        return self.object


# GASTO ---------------------------------------
@login_required
def registrar_gasto(request):
    form = FormGasto(request.POST, request.FILES)

    if form.is_valid():
        gasto = form.save(commit=False)
        gasto.do_locador = request.user
        gasto.save()
        messages.success(request, "Gasto registrado com sucesso!")
        if 'form3' in request.session:
            del request.session['form3']
        return redirect(request.META['HTTP_REFERER'])
    else:
        request.session['form3'] = request.POST
        messages.error(request, "Formulário inválido!")
        return redirect(request.META['HTTP_REFERER'])


class EditarGasto(LoginRequiredMixin, UpdateView):
    model = Gasto
    template_name = 'editar_gasto.html'
    form_class = FormGasto

    def get_initial(self):
        return {'data': self.object.data.strftime('%Y-%m-%d')}

    def get_success_url(self):
        return reverse_lazy('home:Gastos', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Gasto, pk=self.kwargs['pk'], do_locador=self.request.user)
        return self.object


class ExcluirGasto(LoginRequiredMixin, DeleteView):
    model = Gasto
    template_name = 'excluir_item.html'

    def get_success_url(self):
        return reverse_lazy('home:Gastos', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Gasto, pk=self.kwargs['pk'], do_locador=self.request.user)
        return self.object


# LOCATARIO ---------------------------------------
@login_required
def registrar_locat(request):
    form = FormLocatario(request.POST, request.FILES)
    if form.is_valid():
        locatario = form.save(commit=False)
        locatario.do_locador = request.user
        locatario.save()
        messages.success(request, "Locatário registrado com sucesso!")
        if 'form4' in request.session:
            del request.session['form4']
        return redirect(request.META['HTTP_REFERER'])
    else:
        request.session['form4'] = request.POST
        messages.error(request, f"Formulário inválido!")
        return redirect(request.META['HTTP_REFERER'])


# CONTRATO ---------------------------------------
@login_required
def registrar_contrato(request):
    form = FormContrato(request.user, request.POST)
    if form.is_valid():
        contrato = form.save(commit=False)
        contrato.do_locador = request.user
        contrato.save()
        messages.success(request, "Contrato resgistrado com sucesso!")
        if 'form5' in request.session:
            del request.session['form5']
        return redirect(request.META['HTTP_REFERER'])
    else:
        request.session['form5'] = request.POST
        messages.error(request, "Formulário inválido!")
        return redirect(request.META['HTTP_REFERER'])


@login_required
def rescindir_contrat(request, pk):
    contrato = Contrato.objects.get(pk=pk)
    if contrato.do_locador == request.user:
        if contrato.rescindido is True:
            contrato.rescindido = False
            contrato.save()
            return redirect(request.META['HTTP_REFERER'])
        else:
            contrato.data_de_rescisao = timezone.now()
            data = dateformat.format(timezone.now(), 'd-m-Y')
            contrato.rescindido = True
            contrato.save()
            messages.warning(request, f"Contrato rescindido com sucesso! Registro criado em {data}.")
        return redirect(request.META['HTTP_REFERER'])
    else:
        return Http404


@login_required
def recebido_contrat(request, pk):
    contrato = Contrato.objects.get(pk=pk)
    if contrato.do_locador == request.user:
        if contrato.em_posse is True:
            contrato.em_posse = False
            contrato.save()
            return redirect(request.META['HTTP_REFERER'])
        else:
            contrato.em_posse = True
            contrato.save()
            messages.success(request, f"Cópia do contrato do locador em mãos!")
        return redirect(request.META['HTTP_REFERER'])
    else:
        return Http404


# IMOVEL ---------------------------------------
@login_required
def registrar_imovel(request):
    if request.method == 'POST':
        form = FormImovel(request.user, request.POST)
        if form.is_valid():
            imovel = form.save(commit=False)
            imovel.do_locador = request.user
            imovel.save()
            messages.success(request, "Imóvel resgistrado com sucesso!")
            if 'form6' in request.session:
                del request.session['form6']
            return redirect(request.META['HTTP_REFERER'])
        else:
            request.session['form6'] = request.POST
            messages.error(request, "Formulário inválido!")
            return redirect(request.META['HTTP_REFERER'])


# ANOTAÇÃO ---------------------------------------
@login_required
def registrar_anotacao(request):
    form = FormAnotacoes(request.POST)
    if form.is_valid():
        notas = form.save(commit=False)
        notas.do_usuario = request.user
        notas.save()
        messages.success(request, "Anotação resgistrada com sucesso!")
        if 'form7' in request.session:
            del request.session['form7']
        return redirect(request.META['HTTP_REFERER'])
    else:
        request.session['form7'] = request.POST
        messages.error(request, "Formulário inválido!")
        return redirect(request.META['HTTP_REFERER'])


# -=-=-=-=-=-=-=-= BOTÃO GERAR -=-=-=-=-=-=-=-=

def recibos(request, pk):
    form = FormRecibos()
    context = {}

    # Indica se o usuario tem contrato para o template e ja pega o primeiro pra carregar\/
    usuario = Usuario.objects.get(pk=request.user.pk)
    tem_contratos = Contrato.objects.filter(do_locador=request.user.pk).order_by('-data_registro').first()

    if tem_contratos:
        contrato = tem_contratos

        # Indica para o template se o usuário prenencheu os dados necessários para gerar os recibos\/
        pede_dados = False
        if usuario.first_name == '' or usuario.last_name == '' or usuario.CPF == '':
            pede_dados = True
        else:
            if request.user.ultimo_recibo_gerado:
                contrato = Contrato.objects.get(pk=request.user.ultimo_recibo_gerado.pk)

            # Carrega do model do usuario o ultimo recibo salvo no form, se existe\/
            if usuario.ultimo_recibo_gerado:
                form = FormRecibos(initial={'contrato': usuario.ultimo_recibo_gerado})

            # Se for um post, salvar o novo contrato no campo 'ultimo recibo salvo' do usuario\/
            if request.method == 'POST':
                form = FormRecibos(request.POST)
                if form.is_valid():
                    contrato = Contrato.objects.get(pk=form.cleaned_data['contrato'].pk)
                    usuario.ultimo_recibo_gerado = contrato
                    usuario.save(update_fields=['ultimo_recibo_gerado'])

            # Criar o arquivo se não existe ou carregar se existe:
            if contrato.recibos_pdf and path.exists(f'{settings.MEDIA_ROOT}{contrato.recibos_pdf}'):
                pass
            else:
                locatario = contrato.do_locatario
                imovel = contrato.do_imovel

                # Tratamentos
                reais = int(contrato.valor_mensal[:-2])
                centavos = int(contrato.valor_mensal[-2:])
                num_ptbr_reais = num2words(reais, lang='pt-br')
                completo = ''
                if centavos > 0:
                    num_ptbr_centavos = num2words(centavos, lang='pt-br')
                    completo = f' E {num_ptbr_centavos} centavos'
                codigos = list(
                    Parcela.objects.filter(do_contrato=contrato.pk).values("codigo").values_list('codigo', flat=True))
                datas = list(
                    Parcela.objects.filter(do_contrato=contrato.pk).values("data_pagm_ref").values_list('data_pagm_ref',
                                                                                                        flat=True))
                datas_tratadas = list()
                for data in datas:
                    month = data.strftime('%B')
                    year = data.strftime('%Y')
                    datas_tratadas.append(f'{month.upper()}')
                    datas_tratadas.append(f'{year}')

                # Preparar dados para envio
                dados = {'cod_contrato': f'{contrato.codigo}',
                         'nome_locador': f'{usuario.first_name.upper()} {usuario.last_name.upper()}',
                         'rg_locd': f'{usuario.RG}',
                         'cpf_locd': f'{usuario.CPF}',
                         'nome_locatario': f'{locatario.nome.upper()}',
                         'rg_loct': f'{locatario.RG}',
                         'cpf_loct': f'{locatario.CPF}',
                         'valor_e_extenso': f'{contrato.valor_format()} ({num_ptbr_reais.upper()} REAIS{completo.upper()})',
                         'endereco': f"{imovel.endereco_completo()}",
                         'cidade': f'{imovel.cidade}',
                         'data': '________________, ____ de _________ de ________',
                         'cod_recibo': codigos,
                         'mes_e_ano': datas_tratadas,
                         }

                local_temp = gerar_recibos(dados=dados)
                contrato.recibos_pdf = File(local_temp, name=f'recibos de {dados["cod_contrato"]}.pdf')
                contrato.save()

        context = {'form': form, 'contrato': contrato, 'tem_contratos': tem_contratos, 'pede_dados': pede_dados,
                   'SITE_NAME': settings.SITE_NAME}
    return render(request, 'gerar_recibos.html', context)


def tabela(request, pk):
    context = {'SITE_NAME': settings.SITE_NAME}
    usuario = Usuario.objects.get(pk=request.user.pk)
    tem_contratos = True if Contrato.objects.filter(do_locador=request.user.pk).first() else False
    context['tem_contratos'] = tem_contratos

    meses_qtd = 4
    imov_qtd = 8
    comeca_em = datetime.now()

    # Tratamentos
    # Lista de mes/ano cujo início é conforme a escolha do usuario: (iniciar em: 'mes/ano')
    datas = []
    for x in range(0, meses_qtd):
        datas.append((comeca_em + relativedelta(months=x)).strftime("%B/%Y").title())

    # Preparar dados para envio
    dados = {'usuario': usuario, "usuario_username": usuario.username,
             "usuario_nome_compl": f'{str(usuario.first_name).upper()} {str(usuario.last_name).upper()}',
             'imoveis_ativos': Imovei.objects.ocupados().filter(do_locador=request.user).order_by(
                 '-data_registro'), 'datas': datas, 'imov_qtd': imov_qtd}

    if tem_contratos:
        gerar_tabela(dados)
        link = rf'/media/tabela_docs/tabela_{usuario}.pdf'
        context['tabela'] = link

    return render(request, 'gerar_tabela.html', context)


# -=-=-=-=-=-=-=-= BOTÃO HISTORICO -=-=-=-=-=-=-=-=

# PAGAMENTOS ---------------------------------------
class Pagamentos(LoginRequiredMixin, ListView):
    template_name = 'exibir_pagamentos.html'
    model = Pagamento
    context_object_name = 'pagamentos'
    paginate_by = 50

    def get_queryset(self):
        self.object_list = Pagamento.objects.filter(ao_locador=self.request.user).order_by('-data_criacao')
        return self.object_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(Pagamentos, self).get_context_data(**kwargs)
        context['SITE_NAME'] = settings.SITE_NAME
        return context


# GASTOS ---------------------------------------
class Gastos(LoginRequiredMixin, ListView):
    template_name = 'exibir_gastos.html'
    model = Gasto
    context_object_name = 'gastos'
    paginate_by = 30

    def get_queryset(self):
        self.object_list = Gasto.objects.filter(do_locador=self.request.user).order_by('-data_criacao')
        return self.object_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(Gastos, self).get_context_data(**kwargs)
        context['SITE_NAME'] = settings.SITE_NAME
        return context


# GRUPO ---------------------------------------
@login_required
def criar_grupo(request):
    if request.method == "GET":
        grupos = ImovGrupo.objects.all().filter(do_usuario=request.user)
        form = FormimovelGrupo()
        context = {'form': form if ImovGrupo.objects.all().filter(do_usuario=request.user).count() <= 17 else '',
                   'grupos': grupos, 'SITE_NAME': settings.SITE_NAME}
        return render(request, 'criar_grupos.html', context)
    elif request.method == 'POST':
        nome = request.POST.get('nome')
        do_usuario = request.user
        grupo = ImovGrupo(nome=nome, do_usuario=do_usuario)
        grupo.save()
        return redirect(request.META['HTTP_REFERER'])


class EditarGrup(LoginRequiredMixin, UpdateView):
    model = ImovGrupo
    template_name = 'editar_grupo.html'
    form_class = FormimovelGrupo

    def get_success_url(self):
        return reverse_lazy('home:Criar Grupo Imóveis')

    def get_object(self, queryset=None):
        self.object = get_object_or_404(ImovGrupo, pk=self.kwargs['pk'], do_usuario=self.request.user)
        return self.object

    def get_context_data(self, *, object_list=True, **kwargs):
        context = super(EditarGrup, self).get_context_data(**kwargs)
        context['SITE_NAME'] = settings.SITE_NAME
        return context


class ExcluirGrupo(LoginRequiredMixin, DeleteView):
    model = ImovGrupo
    template_name = 'excluir_item.html'

    def get_success_url(self):
        return reverse_lazy('home:Criar Grupo Imóveis')

    def get_object(self, queryset=None):
        self.object = get_object_or_404(ImovGrupo, pk=self.kwargs['pk'], do_usuario=self.request.user)
        return self.object

    def get_context_data(self, *, object_list=True, **kwargs):
        context = super(ExcluirGrupo, self).get_context_data(**kwargs)
        context['SITE_NAME'] = settings.SITE_NAME
        return context


# IMOVEIS ---------------------------------------
class Imoveis(LoginRequiredMixin, ListView):
    template_name = 'exibir_imoveis.html'
    model = Imovei
    context_object_name = 'imoveis'
    paginate_by = 30

    def get_queryset(self):
        self.object_list = Imovei.objects.filter(do_locador=self.request.user).order_by('-data_registro')
        return self.object_list

    def get_context_data(self, *, object_list=True, **kwargs):
        context = super(Imoveis, self).get_context_data(**kwargs)
        context['SITE_NAME'] = settings.SITE_NAME
        return context


class EditarImov(LoginRequiredMixin, UpdateView):
    model = Imovei
    template_name = 'editar_imovel.html'
    success_url = reverse_lazy('/')
    form_class = FormImovel

    def get_form_kwargs(self, **kwargs):
        form_kwargs = super(EditarImov, self).get_form_kwargs(**kwargs)
        form_kwargs["user"] = self.request.user
        return form_kwargs

    def get_success_url(self):
        return reverse_lazy('home:Imóveis', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Imovei, pk=self.kwargs['pk'], do_locador=self.request.user)
        return self.object

    def get_context_data(self, *, object_list=True, **kwargs):
        context = super(EditarImov, self).get_context_data(**kwargs)
        context['SITE_NAME'] = settings.SITE_NAME
        return context


class ExcluirImov(LoginRequiredMixin, DeleteView):
    model = Imovei
    template_name = 'excluir_item.html'

    def get_success_url(self):
        return reverse_lazy('home:Imóveis', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Imovei, pk=self.kwargs['pk'], do_locador=self.request.user)
        return self.object

    def get_context_data(self, *, object_list=True, **kwargs):
        context = super(ExcluirImov, self).get_context_data(**kwargs)
        context['SITE_NAME'] = settings.SITE_NAME
        return context


# LOCATARIOS ---------------------------------------
class Locatarios(LoginRequiredMixin, ListView):
    template_name = 'exibir_locatarios.html'
    model = Locatario
    context_object_name = 'locatarios'
    paginate_by = 30

    def get_queryset(self):
        self.object_list = Locatario.objects.filter(do_locador=self.request.user).order_by('-data_registro').annotate(
            Count('do_locador'))
        return self.object_list

    def get_context_data(self, *, object_list=True, **kwargs):
        context = super(Locatarios, self).get_context_data(**kwargs)
        context['SITE_NAME'] = settings.SITE_NAME
        return context


class EditarLocat(LoginRequiredMixin, UpdateView):
    model = Locatario
    template_name = 'editar_locatario.html'
    form_class = FormLocatario
    success_url = reverse_lazy('/')

    def get_success_url(self):
        return reverse_lazy('home:Locatários', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Locatario, pk=self.kwargs['pk'], do_locador=self.request.user)
        return self.object

    def get_context_data(self, *, object_list=True, **kwargs):
        context = super(EditarLocat, self).get_context_data(**kwargs)
        context['SITE_NAME'] = settings.SITE_NAME
        return context


class ExcluirLocat(LoginRequiredMixin, DeleteView):
    model = Locatario
    template_name = 'excluir_item.html'

    def get_success_url(self):
        return reverse_lazy('home:Locatários', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Locatario, pk=self.kwargs['pk'], do_locador=self.request.user)
        return self.object

    def get_context_data(self, *, object_list=True, **kwargs):
        context = super(ExcluirLocat, self).get_context_data(**kwargs)
        context['SITE_NAME'] = settings.SITE_NAME
        return context


# CONTRATOS ---------------------------------------
class Contratos(LoginRequiredMixin, ListView):
    template_name = 'exibir_contratos.html'
    model = Contrato
    context_object_name = 'contratos'
    paginate_by = 30

    def get_queryset(self):
        self.object_list = Contrato.objects.filter(do_locador=self.request.user).order_by('-data_registro')
        return self.object_list

    def get_context_data(self, *, object_list=True, **kwargs):
        context = super(Contratos, self).get_context_data(**kwargs)
        context['SITE_NAME'] = settings.SITE_NAME
        return context


class EditarContrato(LoginRequiredMixin, UpdateView):
    model = Contrato
    template_name = 'editar_contrato.html'
    form_class = FormContrato
    success_url = reverse_lazy('/')

    def get_initial(self):
        return {'data_entrada': self.object.data_entrada.strftime('%Y-%m-%d')}

    def get_form_kwargs(self, **kwargs):
        form_kwargs = super(EditarContrato, self).get_form_kwargs(**kwargs)
        form_kwargs["user"] = self.request.user
        return form_kwargs

    def get_success_url(self):
        contrato = Contrato.objects.get(pk=self.object.pk)
        contrato.recibos_pdf.delete()
        contrato.save()
        return reverse_lazy('home:Contratos', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Contrato, pk=self.kwargs['pk'], do_locador=self.request.user)
        return self.object

    def get_context_data(self, *, object_list=True, **kwargs):
        context = super(EditarContrato, self).get_context_data(**kwargs)
        context['SITE_NAME'] = settings.SITE_NAME
        return context


class ExcluirContrato(LoginRequiredMixin, DeleteView):
    model = Contrato
    template_name = 'excluir_item.html'

    def get_success_url(self):
        imov_do_contrato = Contrato.objects.get(pk=self.kwargs['pk']).do_imovel.pk
        imovel = Imovei.objects.get(pk=imov_do_contrato)
        imovel.com_locatario = None
        imovel.save()
        return reverse_lazy('home:Contratos', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Contrato, pk=self.kwargs['pk'], do_locador=self.request.user)
        return self.object

    def get_context_data(self, *, object_list=True, **kwargs):
        context = super(ExcluirContrato, self).get_context_data(**kwargs)
        context['SITE_NAME'] = settings.SITE_NAME
        return context


# ANOTAÇÕES ---------------------------------------
class Notas(LoginRequiredMixin, ListView):
    template_name = 'exibir_anotacao.html'
    model = Anotacoe
    context_object_name = 'anotacoes'
    paginate_by = 26
    form_class = FormAnotacoes

    def get_queryset(self):
        self.object_list = Anotacoe.objects.filter(do_usuario=self.request.user).order_by('-data_registro')
        return self.object_list

    def get_context_data(self, *, object_list=True, **kwargs):
        context = super(Notas, self).get_context_data(**kwargs)
        context['SITE_NAME'] = settings.SITE_NAME
        return context


class EditarAnotacao(LoginRequiredMixin, UpdateView):
    model = Anotacoe
    template_name = 'editar_anotacao.html'
    form_class = FormAnotacoes
    success_url = reverse_lazy('/')

    def get_initial(self):
        return {'data_registro': self.object.data_registro.strftime('%Y-%m-%d')}

    def get_success_url(self):
        return reverse_lazy('home:Anotações', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Anotacoe, pk=self.kwargs['pk'], do_usuario=self.request.user)
        return self.object

    def get_context_data(self, *, object_list=True, **kwargs):
        context = super(EditarAnotacao, self).get_context_data(**kwargs)
        context['SITE_NAME'] = settings.SITE_NAME
        return context


class ExcluirAnotacao(LoginRequiredMixin, DeleteView):
    model = Anotacoe
    template_name = 'excluir_item.html'

    def get_success_url(self):
        return reverse_lazy('home:Anotações', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Anotacoe, pk=self.kwargs['pk'], do_usuario=self.request.user)
        return self.object

    def get_context_data(self, *, object_list=True, **kwargs):
        context = super(ExcluirAnotacao, self).get_context_data(**kwargs)
        context['SITE_NAME'] = settings.SITE_NAME
        return context


# -=-=-=-=-=-=-=-= USUARIO -=-=-=-=-=-=-=-=

class Homepage(FormView):
    template_name = 'home.html'
    form_class = FormHomePage

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(f'dashboard/{request.user.id}')
        else:
            return super().get(request, *args, **kwargs)

    def get_success_url(self):
        email = self.request.POST.get('email')
        usuarios = Usuario.objects.filter(email=email)
        if usuarios:
            return reverse('home:Login')
        else:
            return reverse('home:Criar Conta')

    def get_context_data(self, *, object_list=True, **kwargs):
        context = super(Homepage, self).get_context_data(**kwargs)
        context['SITE_NAME'] = settings.SITE_NAME
        return context


class CriarConta(CreateView):
    template_name = 'criar_conta.html'
    form_class = FormCriarConta
    success_url = reverse_lazy('home:Login')

    def get_form(self, form_class=None):
        form = super(CriarConta, self).get_form(form_class)
        form.fields['email'].required = True
        return form

    def get_context_data(self, *, object_list=True, **kwargs):
        context = super(CriarConta, self).get_context_data(**kwargs)
        context['SITE_NAME'] = settings.SITE_NAME
        return context


class EditarPerfil(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    template_name = 'editar_perfil.html'
    model = Usuario
    fields = ['username', 'first_name', 'last_name', 'email', 'telefone', 'RG', 'CPF']

    def get_form(self, form_class=None):
        form = super(EditarPerfil, self).get_form(form_class)
        form.fields['first_name'].required = True
        form.fields['last_name'].required = True
        form.fields['CPF'].required = True
        return form

    def get_success_url(self):
        return reverse("home:DashBoard", kwargs={"pk": self.request.user.pk})

    def get_success_message(self, cleaned_data):
        success_message = 'Perfil editado com sucesso!'
        return success_message

    def get_object(self):
        return self.request.user

    def get_context_data(self, *, object_list=True, **kwargs):
        context = super(EditarPerfil, self).get_context_data(**kwargs)
        context['SITE_NAME'] = settings.SITE_NAME
        return context


class ApagarConta(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    template_name = 'excluir_conta.html'
    model = Usuario
    success_message = 'Conta apagada'
    success_url = reverse_lazy('home:home')

    def get_object(self):
        return self.request.user

    def get_context_data(self, *, object_list=True, **kwargs):
        context = super(ApagarConta, self).get_context_data(**kwargs)
        context['SITE_NAME'] = settings.SITE_NAME
        return context


# -=-=-=-=-=-=-=-= OUTROS -=-=-=-=-=-=-=-=

@login_required
def mensagem_desenvolvedor(request):
    form = FormMensagem(request.POST, request.FILES)
    if form.is_valid():
        mensagem = form.save(commit=False)
        mensagem.do_usuario = request.user
        mensagem.save()
        messages.success(request, "Mensagem enviada com sucesso!")
        return redirect(request.META['HTTP_REFERER'])
    else:
        request.session['form2'] = request.POST
        messages.error(request, "Formulário inválido!")
        return redirect(request.META['HTTP_REFERER'])


@login_required
def botaoteste(request):
    form_adm = FormAdmin(request.POST, initial={'p_usuario': request.user})
    fict_qtd = settings.FICT_QTD
    executar = fict_multi = int
    if form_adm.is_valid():
        usuario = form_adm.cleaned_data['p_usuario']
        fict_multi = int(form_adm.data['multiplicar_por'])
        executar = int(form_adm.data['executar'])

    if executar == 170:
        messages.success(request, f"Teste")

    if executar == 1 or executar == 100:
        count = 0
        for x in range(fict_multi * fict_qtd['locatario']):
            count += 1
            aleatorio = locatarios_ficticios()
            form = FormLocatario()
            locatario = form.save(commit=False)
            locatario.do_locador = usuario
            locatario.nome = aleatorio.get('nome')
            locatario.RG = aleatorio.get('RG')
            locatario.CPF = aleatorio.get('CPF')
            locatario.ocupacao = aleatorio.get('ocupacao')
            locatario.telefone1 = aleatorio.get('telefone1')
            locatario.telefone2 = aleatorio.get('telefone2')
            locatario.email = aleatorio.get('email')
            locatario.nacionalidade = aleatorio.get('nacionalidade')
            locatario.estadocivil = aleatorio.get('estadocivil')
            locatario.save()
        messages.success(request, f"Criados {count} locatário")

    if executar == 160 or executar == 100:
        if ImovGrupo.objects.filter(do_usuario=usuario).count() < fict_qtd['imovel_g'] or executar == 160:
            count = 0
            for x in range(fict_multi if executar == 160 else 1 * fict_qtd['imovel_g']):
                count += 1
                aleatorio = imov_grupo_fict()
                form = FormimovelGrupo()
                imovel_g = form.save(commit=False)
                imovel_g.do_usuario = usuario
                imovel_g.nome = aleatorio.get('nome')
                imovel_g.save()
            messages.success(request, f"Criados {count} grupos")

    if executar == 2 or executar == 100:
        if ImovGrupo.objects.filter(do_usuario=usuario).count() > 0:
            count = 0
            for x in range(fict_multi * fict_qtd['imovel']):
                count += 1
                aleatorio = imoveis_ficticios()
                form = FormImovel(usuario)
                imovel = form.save(commit=False)
                imovel.do_locador = usuario
                imovel.nome = aleatorio.get('nome')
                imovel.grupo = aleatorio.get('grupo')
                imovel.cep = aleatorio.get('cep')
                imovel.endereco = aleatorio.get('endereco')
                imovel.numero = aleatorio.get('numero')
                imovel.complemento = aleatorio.get('complemento')
                imovel.bairro = aleatorio.get('bairro')
                imovel.cidade = aleatorio.get('cidade')
                imovel.estado = aleatorio.get('estado')
                imovel.uc_energia = aleatorio.get('uc_energia')
                imovel.uc_agua = aleatorio.get('uc_agua')
                imovel.data_registro = aleatorio.get('data_registro')
                imovel.save()
            messages.success(request, f"Criados {count} imoveis")
        else:
            messages.error(request, "Primeiro crie grupos")

    if executar == 3 or executar == 100:
        if Imovei.objects.filter(do_locador=usuario).count() > 0 and \
                Locatario.objects.filter(do_locador=usuario).count() > 0:
            count = 0
            for x in range(fict_multi * fict_qtd['contrato']):
                count += 1
                aleatorio = contratos_ficticios(request, usuario)
                form = FormContrato(usuario)
                contrato = form.save(commit=False)
                contrato.do_locador = usuario
                contrato.em_posse = True
                contrato.do_locatario = aleatorio.get('do_locatario')
                contrato.do_imovel = aleatorio.get('do_imovel')
                contrato.data_entrada = aleatorio.get('data_entrada')
                contrato.duracao = aleatorio.get('duracao')
                contrato.valor_mensal = aleatorio.get('valor_mensal')
                contrato.dia_vencimento = aleatorio.get('dia_vencimento')
                contrato.save()
            messages.success(request, f"Criados {count} contratos")
        else:
            messages.error(request, "Primeiro crie imóveis e locatários")

    if executar == 4 or executar == 100:
        if Contrato.objects.filter(do_locador=usuario).count() > 0:
            count = 0
            for x in range(fict_multi * fict_qtd['pagamento']):
                count += 1
                aleatorio = pagamentos_ficticios()
                form = FormPagamento(usuario)
                pagamento = form.save(commit=False)
                locatario = Contrato.objects.get(pk=aleatorio.get('ao_contrato').pk).do_locatario
                pagamento.ao_locador = usuario
                pagamento.do_locatario = locatario
                pagamento.ao_contrato = aleatorio.get('ao_contrato')
                pagamento.valor_pago = aleatorio.get('valor_pago')
                pagamento.data_pagamento = aleatorio.get('data_pagamento')
                pagamento.forma = aleatorio.get('forma')
                pagamento.recibo = aleatorio.get('recibo')
                pagamento.save()
            messages.success(request, f"Criados {count} pagamentos")
        else:
            messages.error(request, "Primeiro crie contratos")

    if executar == 5 or executar == 100:
        if Imovei.objects.filter(do_locador=usuario).count() > 0:
            count = 0
            for x in range(fict_multi * fict_qtd['gasto']):
                count += 1
                aleatorio = gastos_ficticios()
                form = FormGasto()
                gasto = form.save(commit=False)
                gasto.do_locador = usuario
                gasto.do_imovel = aleatorio.get('do_imovel')
                gasto.valor = aleatorio.get('valor')
                gasto.data = aleatorio.get('data')
                gasto.observacoes = aleatorio.get('observacoes')
                gasto.save()
            messages.success(request, f"Criados {count} gastos")
        else:
            messages.error(request, "Primeiro crie imóveis")

    if executar == 6 or executar == 100:
        count = 0
        for x in range(fict_multi * fict_qtd['nota']):
            count += 1
            aleatorio = anotacoes_ficticias()
            form = FormAnotacoes()
            nota = form.save(commit=False)
            nota.do_usuario = usuario
            nota.titulo = aleatorio.get('titulo')
            nota.data_registro = aleatorio.get('data_registro')
            nota.texto = aleatorio.get('texto')
            nota.save()
        messages.success(request, f"Criadas {count} anotações")

    if executar == 150:
        count = 0
        for x in range(fict_multi * fict_qtd['user']):
            aleatorio = usuarios_ficticios()
            UserModel = get_user_model()
            if not UserModel.objects.filter(username=aleatorio.get('username')).exists():
                count += 1
                user = UserModel.objects.create_user(aleatorio.get('username'), password=aleatorio.get('password'))
                user.is_superuser = False
                user.is_staff = False
                user.first_name = aleatorio.get('first_name')
                user.last_name = aleatorio.get('last_name')
                user.email = aleatorio.get('email')
                user.telefone = aleatorio.get('telefone')
                user.RG = aleatorio.get('RG')
                user.CPF = aleatorio.get('CPF')
                user.save()
        messages.success(request, f"Criadas {count} usuários")

    return redirect(request.META['HTTP_REFERER'])
