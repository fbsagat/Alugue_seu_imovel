from django.urls import path
from financeiro.views import pagar_pacote


app_name = 'home'

urlpatterns = [
    path('pagar_pacote/<int:pacote_index>/<str:forma>', pagar_pacote, name='Pagar Pacote'),
]
