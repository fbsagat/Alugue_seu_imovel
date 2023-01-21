from django.urls import path
from navbar.views import Dashboard, Locatarios, Imoveis, Contratos, \
    registrar_pagamento, registrar_imovel, registrar_anotacao, registrar_contrato, registrar_locat, EditarLocat, \
    ExcluirLocat, registrar_gasto, Pagamentos, Gastos, Notas, EditarGrup, ExcluirGrupo, EditarImov, \
    ExcluirImov, criar_grupo, rescindir_contrat, recebido_contrat, entregar_recibo, ExcluirPagm, EditarContrato, \
    ExcluirContrato, EditarGasto, ExcluirGasto, EditarAnotacao, ExcluirAnotacao

app_name = 'navbar'

urlpatterns = [
    # PAG VISUALIZAÇÃO -------------------
    path('dashboard/<int:pk>', Dashboard.as_view(), name='DashBoard'),
    path('pagamentos/<int:pk>', Pagamentos.as_view(), name='Pagamentos'),
    path('gastos/<int:pk>', Gastos.as_view(), name='Gastos'),
    path('locatarios/<int:pk>', Locatarios.as_view(), name='Locatários'),
    path('imoveis/<int:pk>', Imoveis.as_view(), name='Imóveis'),
    path('anotacoes/<int:pk>', Notas.as_view(), name='Anotações'),
    path('contratos/<int:pk>', Contratos.as_view(), name='Contratos'),

    # REGISTROS -------------------

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
]
