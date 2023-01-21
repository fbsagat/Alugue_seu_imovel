from django.shortcuts import redirect, render
from django.utils import timezone, dateformat
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DeleteView, UpdateView, ListView
from home.models import Locatario, Imovei, Contrato, Pagamento, Gasto, Anotacoe, ImovGrupo, Usuario
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import messages
from django.contrib.auth.decorators import login_required
from navbar.forms import FormPagamento, FormGasto, FormLocatario, FormImovel, FormAnotacoes, FormContrato, \
    FormimovelGrupo
from django.shortcuts import get_object_or_404, Http404

from django.db.models.aggregates import Count, Sum, Avg, Max, Min
from django.db.models import Q, F, Value
from django.db.models import Window, F
from django.db.models.functions import DenseRank


# -=-=-=-=-=-=-=-= BOTÃO DASHBOARD -=-=-=-=-=-=-=-=

class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = 'exibir_dashboard.html'
    model = Locatario


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
        return redirect(request.META['HTTP_REFERER'])
    else:
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
        return reverse_lazy('navbar:Pagamentos', args=[self.request.user.id])

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
        return redirect(request.META['HTTP_REFERER'])
    else:
        messages.error(request, "Formulário inválido!")
        return redirect(request.META['HTTP_REFERER'])


class EditarGasto(LoginRequiredMixin, UpdateView):
    model = Gasto
    template_name = 'editar_gasto.html'
    form_class = FormGasto

    def get_success_url(self):
        return reverse_lazy('navbar:Gastos', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Gasto, pk=self.kwargs['pk'], do_locador=self.request.user)
        return self.object


class ExcluirGasto(LoginRequiredMixin, DeleteView):
    model = Gasto
    template_name = 'excluir_item.html'

    def get_success_url(self):
        return reverse_lazy('navbar:Gastos', kwargs={'pk': self.object.pk})

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
        return redirect(request.META['HTTP_REFERER'])
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
        return redirect(request.META['HTTP_REFERER'])
    else:
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
            return redirect(request.META['HTTP_REFERER'])
        else:
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
        return redirect(request.META['HTTP_REFERER'])
    else:
        messages.error(request, "Formulário inválido!")
        return redirect(request.META['HTTP_REFERER'])


# -=-=-=-=-=-=-=-= BOTÃO VISUALIZAR -=-=-=-=-=-=-=-=

# PAGAMENTOS ---------------------------------------
class Pagamentos(LoginRequiredMixin, ListView):
    template_name = 'exibir_pagamentos.html'
    model = Pagamento
    context_object_name = 'pagamentos'
    paginate_by = 50

    def get_queryset(self):
        self.object_list = Pagamento.objects.filter(ao_locador=self.request.user).order_by('-data_criacao')
        return self.object_list


# GASTOS ---------------------------------------
class Gastos(LoginRequiredMixin, ListView):
    template_name = 'exibir_gastos.html'
    model = Gasto
    context_object_name = 'gastos'
    paginate_by = 30

    def get_queryset(self):
        self.object_list = Gasto.objects.filter(do_locador=self.request.user).order_by('-data_criacao')
        return self.object_list


# GRUPO ---------------------------------------
@login_required
def criar_grupo(request):
    if request.method == "GET":
        grupos = ImovGrupo.objects.all().filter(do_usuario=request.user)
        form = FormimovelGrupo()
        context = {'form': form if ImovGrupo.objects.all().filter(do_usuario=request.user).count() <= 17 else '',
                   'grupos': grupos}
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
        return reverse_lazy('navbar:Criar Grupo Imóveis')

    def get_object(self, queryset=None):
        self.object = get_object_or_404(ImovGrupo, pk=self.kwargs['pk'], do_usuario=self.request.user)
        return self.object


class ExcluirGrupo(LoginRequiredMixin, DeleteView):
    model = ImovGrupo
    template_name = 'excluir_item.html'

    def get_success_url(self):
        return reverse_lazy('navbar:Criar Grupo Imóveis')

    def get_object(self, queryset=None):
        self.object = get_object_or_404(ImovGrupo, pk=self.kwargs['pk'], do_usuario=self.request.user)
        return self.object


# IMOVEIS ---------------------------------------
class Imoveis(LoginRequiredMixin, ListView):
    template_name = 'exibir_imoveis.html'
    model = Imovei
    context_object_name = 'imoveis'
    paginate_by = 30

    def get_queryset(self):
        self.object_list = Imovei.objects.filter(do_locador=self.request.user).order_by('-data_registro')
        return self.object_list


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
        return reverse_lazy('navbar:Imóveis', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Imovei, pk=self.kwargs['pk'], do_locador=self.request.user)
        return self.object


class ExcluirImov(LoginRequiredMixin, DeleteView):
    model = Imovei
    template_name = 'excluir_item.html'

    def get_success_url(self):
        return reverse_lazy('navbar:Imóveis', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Imovei, pk=self.kwargs['pk'], do_locador=self.request.user)
        return self.object


# LOCATARIOS ---------------------------------------
class Locatarios(LoginRequiredMixin, ListView):
    template_name = 'exibir_locatarios.html'
    model = Locatario
    context_object_name = 'locatarios'
    paginate_by = 30

    def get_queryset(self):
        self.object_list = Locatario.objects.filter(do_locador=self.request.user).order_by('-data_registro').annotate(Count('do_locador'))
        return self.object_list


class EditarLocat(LoginRequiredMixin, UpdateView):
    model = Locatario
    template_name = 'editar_locatario.html'
    form_class = FormLocatario
    success_url = reverse_lazy('/')

    def get_success_url(self):
        return reverse_lazy('navbar:Locatários', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Locatario, pk=self.kwargs['pk'], do_locador=self.request.user)
        return self.object


class ExcluirLocat(LoginRequiredMixin, DeleteView):
    model = Locatario
    template_name = 'excluir_item.html'

    def get_success_url(self):
        return reverse_lazy('navbar:Locatários', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Locatario, pk=self.kwargs['pk'], do_locador=self.request.user)
        return self.object


# CONTRATOS ---------------------------------------
class Contratos(LoginRequiredMixin, ListView):
    template_name = 'exibir_contratos.html'
    model = Contrato
    context_object_name = 'contratos'
    paginate_by = 30

    def get_queryset(self):
        self.object_list = Contrato.objects.filter(do_locador=self.request.user).order_by('-data_registro')
        return self.object_list


class EditarContrato(LoginRequiredMixin, UpdateView):
    model = Contrato
    template_name = 'editar_contrato.html'
    form_class = FormContrato
    success_url = reverse_lazy('/')

    def get_form_kwargs(self, **kwargs):
        form_kwargs = super(EditarContrato, self).get_form_kwargs(**kwargs)
        form_kwargs["user"] = self.request.user
        return form_kwargs

    def get_success_url(self):
        return reverse_lazy('navbar:Contratos', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Contrato, pk=self.kwargs['pk'], do_locador=self.request.user)
        return self.object


class ExcluirContrato(LoginRequiredMixin, DeleteView):
    model = Contrato
    template_name = 'excluir_item.html'

    def delete(self, request, *args, **kwargs):
        return super().delete(self, request, *args, **kwargs)

    def get_success_url(self):
        imov_do_contrato = Contrato.objects.get(pk=self.kwargs['pk']).do_imovel.pk
        imovel = Imovei.objects.get(pk=imov_do_contrato)
        imovel.com_locatario = None
        imovel.save()
        return reverse_lazy('navbar:Contratos', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Contrato, pk=self.kwargs['pk'], do_locador=self.request.user)
        return self.object


# ANOTAÇÕES ---------------------------------------
class Notas(LoginRequiredMixin, ListView):
    template_name = 'exibir_anotacao.html'
    model = Anotacoe
    context_object_name = 'anotacoes'
    paginate_by = 26

    def get_queryset(self):
        self.object_list = Anotacoe.objects.filter(do_usuario=self.request.user).order_by('-data_registro')
        return self.object_list


class EditarAnotacao(LoginRequiredMixin, UpdateView):
    model = Anotacoe
    template_name = 'editar_anotacao.html'
    form_class = FormAnotacoes
    success_url = reverse_lazy('/')

    def get_success_url(self):
        return reverse_lazy('navbar:Anotações', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Anotacoe, pk=self.kwargs['pk'], do_usuario=self.request.user)
        return self.object


class ExcluirAnotacao(LoginRequiredMixin, DeleteView):
    model = Anotacoe
    template_name = 'excluir_item.html'

    def get_success_url(self):
        return reverse_lazy('navbar:Anotações', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Anotacoe, pk=self.kwargs['pk'], do_usuario=self.request.user)
        return self.object
