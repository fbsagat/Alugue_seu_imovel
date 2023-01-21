from django.urls import path
from django.urls import reverse_lazy
from home.views import ApagarConta, Homepage, CriarConta, EditarPerfil, mensagem_desenvolvedor, botaoteste, Perfil1, \
    Perfil2, Perfil3, eventos
from django.contrib.auth import views as auth_view

app_name = 'home'

urlpatterns = [
    path('', Homepage.as_view(), name='home'),
    path('criarconta/', CriarConta.as_view(), name='Criar Conta'),
    path('apagarconta/<int:pk>/', ApagarConta.as_view(), name='Apagar Conta'),
    path('mudarsenha/', auth_view.PasswordChangeView.as_view(
        template_name='editar_perfil.html', success_url=reverse_lazy('home:home')), name='Mudar Senha'),
    path('eventos/<int:pk>', eventos, name='Eventos'),
    path('Checkimoveis/<int:pk>', Perfil1.as_view(), name='Check Imóveis'),
    path('Checklocatarios/<int:pk>', Perfil2.as_view(), name='Check Locatários'),
    path('Checkcontratos/<int:pk>', Perfil3.as_view(), name='Check Contratos'),
    path('editarperfil/<int:pk>', EditarPerfil.as_view(), name='Editar Perfil'),
    path('login/', auth_view.LoginView.as_view(template_name='Login.html'), name='Login'),
    path('logout/', auth_view.LogoutView.as_view(), name='Logout'),
    path('msgm', mensagem_desenvolvedor, name='Mensagem pro Desenvolvedor'),
    path('botao', botaoteste, name='botaoteste'),
]
