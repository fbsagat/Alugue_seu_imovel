from django.urls import path
from financeiro.views import create_checkout_session, compra_sucesso, compra_cancelada, stripe_webhook, \
    historico_de_compras

app_name = 'financeiro'

urlpatterns = [
    # path('pagar_pacote/<int:pacote_index>/<str:forma>', pagamentos_enviar_webhook, name='Enviar Webhook'),
    # path('webhook/', pagamentos_receber_webhook, name='Receber Webhook'),
    path('historico_de_compras', historico_de_compras, name='Painel Histórico'),
    path('create-checkout-session/<int:pacote_index>/<str:forma>', create_checkout_session, name='Criar Checkout'),
    path('compra_sucesso/<int:pk>', compra_sucesso, name='Compra Sucesso'),
    path('compra_cancelada/', compra_cancelada, name='Compra Cancelada'),
    path('stripe_webhook/', stripe_webhook, name='Stripe webhook'),
]
