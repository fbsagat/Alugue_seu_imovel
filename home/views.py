import locale

from Adm_de_Locacao import settings
from datetime import datetime, date, timedelta, time

from django.shortcuts import redirect, reverse, render
from django.urls import reverse_lazy
from django.db.models.aggregates import Sum
from django.views.generic import CreateView, DeleteView, FormView, UpdateView, ListView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin, messages
from django.contrib.auth.decorators import login_required

from home.funcoes_proprias import valor_br
from home.fakes_test import locatarios_ficticios, imoveis_ficticios, imov_grupo_fict, contratos_ficticios, \
    pagamentos_ficticios, gastos_ficticios, anotacoes_ficticias, usuarios_ficticios
from home.models import Usuario, Imovei, Locatario, Contrato, Pagamento, Gasto, Anotacoe, Recibo
from home.forms import FormCriarConta, FormHomePage, FormMensagem, FormEventos, FormAdmin, FormUsuario
from navbar.forms import FormLocatario, FormImovel, FormimovelGrupo, ImovGrupo, FormContrato, FormPagamento, FormGasto, \
    FormAnotacoes


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


@login_required
def eventos(request, pk):
    user = Usuario.objects.get(pk=request.user.pk)
    form = FormEventos()
    pagamentos = gastos = locatarios = contratos = imoveis = anotacoes = pg_tt = gasto_tt = contr_tt = pag_m_gast = ''
    agreg_1 = agreg_2 = int()
    pesquisa_req = True if user.data_eventos_i and user.itens_eventos and user.qtd_eventos and user.ordem_eventos else False

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
            pg_tt = f'{valor_br(str(agreg_1["total"]))}'

    if '2' in itens_eventos and pesquisa_req:
        gastos = Gasto.objects.filter(do_locador=request.user, data__range=[data_eventos_i, data_eventos_f]).order_by(
            f'{ordem}data')[:qtd_eventos]
        agreg_2 = gastos.aggregate(total=Sum("valor"))
        if agreg_1["total"]:
            gasto_tt = f'{valor_br(str(agreg_2["total"]))}'

    if '1' and '2' in itens_eventos and pesquisa_req and agreg_1["total"] and agreg_2["total"]:
        pag_m_gast = valor_br(str(agreg_1["total"] - agreg_2["total"]))

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
            contr_tt = f'{valor_br(str(contratotal))}'

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
               'contr_tt': contr_tt, 'pag_m_gast': pag_m_gast}

    return render(request, 'exibir_eventos.html', context)


class Perfil1(LoginRequiredMixin, ListView):
    template_name = 'perfil_usuario.html'
    model = Imovei
    context_object_name = 'imoveis'
    paginate_by = 9

    def get_queryset(self):
        self.object_list = Imovei.objects.ocupados().filter(do_locador=self.request.user).order_by('-data_registro')
        return self.object_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(Perfil1, self).get_context_data(**kwargs)
        context['imoveis_qtd'] = Imovei.objects.ocupados().filter(do_locador=self.request.user).count()
        return context


class Perfil2(LoginRequiredMixin, ListView):
    template_name = 'perfil_usuario.html'
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
        return context


class Perfil3(LoginRequiredMixin, ListView):
    template_name = 'perfil_usuario.html'
    model = Contrato
    context_object_name = 'contratos'
    paginate_by = 9

    def get_queryset(self):
        self.object_list = Contrato.objects.filter(do_locador=self.request.user).order_by('-data_registro')
        return self.object_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(Perfil3, self).get_context_data(**kwargs)
        context['contrato_qtd'] = Contrato.objects.filter(do_locador=self.request.user).count()
        return context


class CriarConta(CreateView):
    template_name = 'criar_conta.html'
    form_class = FormCriarConta
    success_url = reverse_lazy('home:Login')


class EditarPerfil(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    template_name = 'editar_perfil.html'
    model = Usuario
    fields = ['username', 'first_name', 'last_name', 'email', 'telefone', 'RG', 'CPF']

    def get_success_url(self):
        return reverse("navbar:DashBoard", kwargs={"pk": self.request.user.pk})

    def get_success_message(self, cleaned_data):
        success_message = 'Perfil editado com sucesso!'
        return success_message

    def get_object(self):
        return self.request.user


class ApagarConta(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    template_name = 'excluir_conta.html'
    model = Usuario
    success_message = 'Conta apagada'
    success_url = reverse_lazy('home:home')

    def get_object(self):
        return self.request.user


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
        if ImovGrupo.objects.filter(do_usuario=usuario).count() < 4 or executar == 160:
            count = 0
            for x in range(fict_multi * fict_qtd['imovel_g']):
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
                user.save()
        messages.success(request, f"Criadas {count} usuários")

    return redirect(request.META['HTTP_REFERER'])
