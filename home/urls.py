from django.urls import path, re_path
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_view

from home.views import visao_geral, Locatarios, Imoveis, Contratos, \
    registrar_pagamento, registrar_imovel, registrar_anotacao, registrar_contrato, registrar_locat, EditarLocat, \
    ExcluirLocat, registrar_gasto, Pagamentos, Gastos, Notas, EditarGrup, ExcluirGrupo, EditarImov, \
    ExcluirImov, criar_grupo, rescindir_contrat, recebido_contrat, entregar_recibo, ExcluirPagm, EditarContrato, \
    ExcluirContrato, EditarGasto, ExcluirGasto, EditarAnotacao, ExcluirAnotacao, recibos, ApagarConta, Homepage, \
    CriarConta, EditarPerfil, mensagem_desenvolvedor, botaoteste, ImoveisAtivos, \
    LocatariosAtivos, ContratosAtivos, eventos, tabela, recibo_entregue, afazer_concluida, gerar_contrato, \
    criar_modelo, EditarModelo, ExcluirModelo, Modelos, forum_sugestoes, \
    like_de_sugestoes, apagar_sugestao, implementar_sugestao, aprovar_sugestao, arquivos_sugestoes_docs, \
    arquivos_locatarios_docs, arquivos_mensagens_ao_dev, arquivos_recibos_docs, arquivos_tabela_docs, \
    arquivos_contrato_docs, aviso_lido

from Alugue_seu_imovel import settings

app_name = 'home'

urlpatterns = [
    # BOTÕES PRINCIPAIS -------------------
    path('visao_geral/', visao_geral, name='Visão Geral'),
    path('eventos/', eventos, name='Eventos'),
    path('imoveis_ativos/', ImoveisAtivos.as_view(), name='Imóveis Ativos'),
    path('locatarios_ativos/', LocatariosAtivos.as_view(), name='Locatários Ativos'),
    path('contratos_ativos/', ContratosAtivos.as_view(), name='Contratos Ativos'),

    # ABA REGISTRAR -------------------

    # PAGAMENTO -------------------
    path('registrar_pagamento', registrar_pagamento, name='Registrar Pagamento'),
    path('entregar_recibo/<int:pk>', entregar_recibo, name='Recibo Entregue'),
    path('excluir_pagamento/<int:pk>', ExcluirPagm.as_view(), name='Excluir Pagamento'),

    # GASTO -------------------
    path('registrar_gasto', registrar_gasto, name='Registrar Gasto'),
    path('editar_registro_de_gasto/<int:pk>', EditarGasto.as_view(), name='Editar Gasto'),
    path('excluir_registro_de_gasto/<int:pk>', ExcluirGasto.as_view(), name='Excluir Gasto'),

    # LOCATARIO -------------------
    path('registro_de_locatario', registrar_locat, name='Registrar Locatario'),
    path('editar_registro_de_locatario/<int:pk>', EditarLocat.as_view(), name='Editar Locatario'),
    path('excluir_registro_de_locatario/<int:pk>', ExcluirLocat.as_view(), name='Excluir Locatario'),

    # CONTRATO -------------------
    path('registrar_contrato', registrar_contrato, name='Registrar Contrato'),
    path('contrato_rescindido/<int:pk>', rescindir_contrat, name='Rescindir Contrato'),
    path('receber_contrato/<int:pk>', recebido_contrat, name='Contrato Recebido'),
    path('editar_contrato/<int:pk>', EditarContrato.as_view(), name='Editar Contrato'),
    path('excluir_contrato/<int:pk>', ExcluirContrato.as_view(), name='Excluir Contrato'),

    # GRUPO -------------------
    path('criar_grupo/', criar_grupo, name='Criar Grupo Imóveis'),
    path('editar_grupo/<int:pk>', EditarGrup.as_view(), name='Editar Grupo Imóveis'),
    path('excluir_grupo/<int:pk>', ExcluirGrupo.as_view(), name='Excluir Grupo Imóveis'),

    # IMOVEL -------------------
    path('registrar_imovel', registrar_imovel, name='Registrar Imóvel'),
    path('editar_regimov/<int:pk>', EditarImov.as_view(), name='Editar Imóvel'),
    path('excluir_regimov/<int:pk>', ExcluirImov.as_view(), name='Excluir Imóvel'),

    # ANOTAÇÕES -------------------
    path('registrar_anotacoes', registrar_anotacao, name='Registrar Anotação'),
    path('editar_anotacao/<int:pk>', EditarAnotacao.as_view(), name='Editar Anotação'),
    path('excluir_anotacao/<int:pk>', ExcluirAnotacao.as_view(), name='Excluir Anotação'),

    # ABA GERAR -------------------
    path('recibos_PDF/', recibos, name='Recibos PDF'),
    path('tabela_PDF/', tabela, name='Tabela PDF'),
    path('contrato_PDF/', gerar_contrato, name='Contrato PDF'),

    # Modelo de contrato:
    path('modelos/', Modelos.as_view(), name='Modelos'),
    path('criar_modelo', criar_modelo, name='Criar Modelo'),
    path('editar_modelo/<int:pk>', EditarModelo.as_view(), name='Editar Modelo'),
    path('excluir_modelo/<int:pk>', ExcluirModelo.as_view(), name='Excluir Modelo'),

    # ABA HISTORICO -------------------
    path('pagamentos/', Pagamentos.as_view(), name='Pagamentos'),
    path('gastos/', Gastos.as_view(), name='Gastos'),
    path('locatarios/', Locatarios.as_view(), name='Locatários'),
    path('imoveis/', Imoveis.as_view(), name='Imóveis'),
    path('anotacoes/', Notas.as_view(), name='Anotações'),
    path('contratos/', Contratos.as_view(), name='Contratos'),

    # AFAZERES -------------------
    path('recibo_entregue/<int:pk>', recibo_entregue, name='Recibo Entregue'),
    path('afazer_concluida/<int:pk>', afazer_concluida, name='Afazer Concluida'),

    # DESENVOLVIMENTO -------------------
    path('msgm/', mensagem_desenvolvedor, name='Mensagem pro Desenvolvedor'),
    path('sugestoes_docs/', forum_sugestoes, name='Sugestões'),
    path('sugestao_like/<int:pk>', like_de_sugestoes, name='like de Sugestão'),
    path('sugestao_apagar/<int:pk>', apagar_sugestao, name='Apagar Sugestão'),
    path('sugestao_implementar/<int:pk>', implementar_sugestao, name='Implementar Sugestão'),
    path('sugestao_aprovar/<int:pk>', aprovar_sugestao, name='Aprovar Sugestão'),

    # AVISOS -------------------
    path('aviso_lido/<int:pk>', aviso_lido, name='Aviso Lido'),

    # GERAL -------------------
    path('', Homepage.as_view(), name='home'),
    path('criar_conta/', CriarConta.as_view(), name='Criar Conta'),
    path('apagar_conta/', ApagarConta.as_view(), name='Apagar Conta'),
    path('mudar_senha/', auth_view.PasswordChangeView.as_view(
        template_name='editar_perfil.html', success_url=reverse_lazy('home:home'),
        extra_context={'SITE_NAME': settings.SITE_NAME}), name='Mudar Senha'),
    path('editar_perfil/', EditarPerfil.as_view(), name='Editar Perfil'),
    path('login/',
         auth_view.LoginView.as_view(template_name='login.html', extra_context={'SITE_NAME': settings.SITE_NAME}),
         name='Login'),
    path('logout/', auth_view.LogoutView.as_view(), name='Logout'),
    path('botao/', botaoteste, name='botaoteste'),


    # SERVIDORES DE ARQUIVOS -------------------
    path('media/sugestoes_docs/<str:year>/<str:month>/<str:file>', arquivos_sugestoes_docs),
    path('media/locatarios_docs/<str:year>/<str:month>/<str:file>', arquivos_locatarios_docs),
    path('media/mensagens_ao_dev/<str:year>/<str:month>/<str:file>', arquivos_mensagens_ao_dev),
    path('media/recibos_docs/<str:year>/<str:month>/<str:file>', arquivos_recibos_docs),
    path('media/tabela_docs/<str:file>', arquivos_tabela_docs),
    path('media/contrato_docs/<str:file>', arquivos_contrato_docs),
]
