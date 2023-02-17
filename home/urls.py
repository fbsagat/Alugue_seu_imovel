from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_view

from home.views import Dashboard, Locatarios, Imoveis, Contratos, \
    registrar_pagamento, registrar_imovel, registrar_anotacao, registrar_contrato, registrar_locat, EditarLocat, \
    ExcluirLocat, registrar_gasto, Pagamentos, Gastos, Notas, EditarGrup, ExcluirGrupo, EditarImov, \
    ExcluirImov, criar_grupo, rescindir_contrat, recebido_contrat, entregar_recibo, ExcluirPagm, EditarContrato, \
    ExcluirContrato, EditarGasto, ExcluirGasto, EditarAnotacao, ExcluirAnotacao, recibos, ApagarConta, Homepage, \
    CriarConta, EditarPerfil, mensagem_desenvolvedor, botaoteste, ImoveisAtivos, \
    LocatariosAtivos, ContratosAtivos, eventos, tabela

from Alugue_seu_imovel import settings

app_name = 'home'

urlpatterns = [
    # BOTÕES PRINCIPAIS -------------------
    path('dashboard/<int:pk>', Dashboard.as_view(), name='DashBoard'),

    # ABA REGISTRAR -------------------

    # PAGAMENTO -------------------
    path('regpag', registrar_pagamento, name='Registrar Pagamento'),
    path('entregarecibo/<int:pk>', entregar_recibo, name='Recibo Entregue'),
    path('excluirpagamento/<int:pk>', ExcluirPagm.as_view(), name='Excluir Pagamento'),

    # GASTO -------------------
    path('reggasto', registrar_gasto, name='Registrar Gasto'),
    path('editarreggasto/<int:pk>', EditarGasto.as_view(), name='Editar Gasto'),
    path('excluirreggasto/<int:pk>', ExcluirGasto.as_view(), name='Excluir Gasto'),

    # LOCATARIO -------------------
    path('reglocat', registrar_locat, name='Registrar Locatario'),
    path('editarreglocat/<int:pk>', EditarLocat.as_view(), name='Editar Locatario'),
    path('excluirreglocat/<int:pk>', ExcluirLocat.as_view(), name='Excluir Locatario'),

    # CONTRATO -------------------
    path('regcontrato', registrar_contrato, name='Registrar Contrato'),
    path('rescindcontrato/<int:pk>', rescindir_contrat, name='Rescindir Contrato'),
    path('receber/<int:pk>', recebido_contrat, name='Contrato Recebido'),
    path('editarcontrato/<int:pk>', EditarContrato.as_view(), name='Editar Contrato'),
    path('excluircontrato/<int:pk>', ExcluirContrato.as_view(), name='Excluir Contrato'),

    # IMOVEL -------------------
    path('regimov', registrar_imovel, name='Registrar Imóvel'),
    path('editarregimov/<int:pk>', EditarImov.as_view(), name='Editar Imóvel'),
    path('excluirregimov/<int:pk>', ExcluirImov.as_view(), name='Excluir Imóvel'),
    # GRUPO -------------------
    path('criargrupo/', criar_grupo, name='Criar Grupo Imóveis'),
    path('editargrupo/<int:pk>', EditarGrup.as_view(), name='Editar Grupo Imóveis'),
    path('excluirgrupo/<int:pk>', ExcluirGrupo.as_view(), name='Excluir Grupo Imóveis'),

    # ANOTAÇÕES -------------------
    path('reganota', registrar_anotacao, name='Registrar Anotação'),
    path('editaranotacao/<int:pk>', EditarAnotacao.as_view(), name='Editar Anotação'),
    path('excluiranotacao/<int:pk>', ExcluirAnotacao.as_view(), name='Excluir Anotação'),

    # ABA GERAR -------------------
    path('recibos/<int:pk>', recibos, name='Recibos'),
    path('tabela/<int:pk>', tabela, name='Tabela'),

    # ABA HISTORICO -------------------
    path('pagamentos/<int:pk>', Pagamentos.as_view(), name='Pagamentos'),
    path('gastos/<int:pk>', Gastos.as_view(), name='Gastos'),
    path('locatarios/<int:pk>', Locatarios.as_view(), name='Locatários'),
    path('imoveis/<int:pk>', Imoveis.as_view(), name='Imóveis'),
    path('anotacoes/<int:pk>', Notas.as_view(), name='Anotações'),
    path('contratos/<int:pk>', Contratos.as_view(), name='Contratos'),

    path('', Homepage.as_view(), name='home'),
    path('criarconta/', CriarConta.as_view(), name='Criar Conta'),
    path('apagarconta/<int:pk>/', ApagarConta.as_view(), name='Apagar Conta'),
    path('mudarsenha/', auth_view.PasswordChangeView.as_view(
        template_name='editar_perfil.html', success_url=reverse_lazy('home:home'),
        extra_context={'SITE_NAME': settings.SITE_NAME}), name='Mudar Senha'),
    path('eventos/<int:pk>', eventos, name='Eventos'),
    path('Checkimoveis/<int:pk>', ImoveisAtivos.as_view(), name='Check Imóveis'),
    path('Checklocatarios/<int:pk>', LocatariosAtivos.as_view(), name='Check Locatários'),
    path('Checkcontratos/<int:pk>', ContratosAtivos.as_view(), name='Check Contratos'),
    path('editarperfil/<int:pk>', EditarPerfil.as_view(), name='Editar Perfil'),
    path('login/',
         auth_view.LoginView.as_view(template_name='Login.html', extra_context={'SITE_NAME': settings.SITE_NAME}),
         name='Login'),
    path('logout/', auth_view.LogoutView.as_view(), name='Logout'),
    path('msgm', mensagem_desenvolvedor, name='Mensagem pro Desenvolvedor'),
    path('botao', botaoteste, name='botaoteste'),
]
