from datetime import datetime, date, timedelta
from django.contrib.auth.forms import UserCreationForm
from django import forms
from home.models import Usuario, MensagemDev
from django.forms import ModelForm
from crispy_forms.bootstrap import InlineCheckboxes
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from Adm_de_Locacao import settings


class Textarea(forms.Textarea):
    input_type = 'text'


class FormAdmin(forms.Form):
    escolhas = (
        ('1', f'Criar {settings.FICT_QTD["locatario"]} Locatários'),
        ('2', f'Criar {settings.FICT_QTD["imovel"]} Imoveis'),
        ('3', f'Criar {settings.FICT_QTD["contrato"]} Contratos'),
        ('4', f'Criar {settings.FICT_QTD["pagamento"]} Pagamentos'),
        ('5', f'Criar {settings.FICT_QTD["gasto"]} Gastos'),
        ('6', f'Criar {settings.FICT_QTD["nota"]} Anotações'),
        ('1000', '-------------'),
        ('100', f'Criar todos acima'),
        ('1000', '-------------'),
        ('150', f'Criar {settings.FICT_QTD["user"]} Usuários'),
        ('160', f'Criar {settings.FICT_QTD["imovel_g"]} Imov_Grupos'),
        ('170', 'Teste Mensagem'),
    )

    executar = forms.ChoiceField(choices=escolhas, initial='100')
    p_usuario = forms.ModelChoiceField(label='', queryset=Usuario.objects.all(),
                                       initial='')
    multiplicar_por = forms.IntegerField(max_value=10, min_value=0, initial=1)

    def __init__(self, *args, **kwargs):
        super(FormAdmin, self).__init__(*args, **kwargs)
        self.fields['multiplicar_por'].widget.attrs.update(style="width: 60px;")
        self.fields['executar'].widget.attrs['class'] = 'mt-1 form-control form-control-sm'
        self.fields['p_usuario'].widget.attrs['class'] = 'mt-1 form-control form-control-sm'
        self.fields['multiplicar_por'].widget.attrs['class'] = 'mt-1 form-control form-control-sm'


class FormUsuario(ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'telefone', 'RG', 'CPF']


mostrar_em_eventos = (
    (1, 'Pagamentos'),
    (2, 'Gastos'),
    (3, 'Locatarios'),
    (4, 'Contratos'),
    (5, 'Imóveis'),
    (6, 'Anotações'),
)

ordem_em_eventos = (
    (1, 'Recentes primeiro'),
    (2, 'Antigos primeiro'),
)


class FormEventos(forms.Form):
    data_eventos_i = forms.DateField(label='A partir de',
                                     widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control-sm'}))

    data_eventos_f = forms.DateField(label='Até', initial=date.today().strftime('%Y-%m-%d'), widget=forms.DateInput(
        attrs={'type': 'date', 'class': 'form-control-sm', 'max': datetime.now().date()}))

    qtd = forms.IntegerField(label='Qtd', max_value=50, min_value=5, step_size=5, initial=10,
                             widget=forms.NumberInput(attrs={'class': 'form-control-sm'}))

    ordem_eventos = forms.ChoiceField(label='Ordem', initial=1, choices=ordem_em_eventos,
                                      widget=forms.RadioSelect())

    itens_eventos = forms.MultipleChoiceField(label='Selecione os itens', choices=mostrar_em_eventos,
                                              initial=[1, 2, 3, 4, 5, 6],
                                              widget=forms.CheckboxSelectMultiple(
                                                  attrs={'choices': mostrar_em_eventos}))

    def __init__(self, *args, **kwargs):
        super(FormEventos, self).__init__(*args, **kwargs)
        self.fields['qtd'].widget.attrs.update(style="width: 65px;")
        self.helper = FormHelper()
        self.helper.layout = Layout(
            InlineCheckboxes('itens_eventos'),
        )


class FormCriarConta(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'telefone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(FormCriarConta, self).__init__(*args, **kwargs)
        self.fields['telefone'].widget.attrs['class'] = 'mask-telefone1'


class FormHomePage(forms.Form):
    email = forms.EmailField(label=False)


class FormMensagem(ModelForm):
    class Meta:
        model = MensagemDev
        exclude = ('do_usuario', 'data_criacao')
        fields = ('tipo_msg', 'titulo', 'mensagem', 'imagem')
        widgets = {
            'mensagem': Textarea(),
        }
