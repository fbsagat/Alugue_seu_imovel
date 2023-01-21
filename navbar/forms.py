from django import forms
from home.models import Pagamento, Gasto, Locatario, Contrato, Imovei, Anotacoe, ImovGrupo
from django.forms import ModelForm


class DateInput(forms.DateInput):
    input_type = 'date'


class Numeros(forms.NumberInput):
    input_type = 'numbers'


class Textarea(forms.Textarea):
    input_type = 'text'


class Mascara(forms.ModelForm):
    class Media:
        js = ('js/jquery.mask.min.js', 'js/custom.js')

    def __init__(self, *args, **kwargs):
        super(Mascara, self).__init__(*args, **kwargs)
        self.fields['telefone1'].widget.attrs['class'] = 'mask-telefone1'
        self.fields['telefone2'].widget.attrs['class'] = 'mask-telefone2'
        self.fields['CPF'].widget.attrs['class'] = 'mask-cpf'


class FormPagamento(ModelForm):
    class Meta:
        model = Pagamento
        fields = ('ao_contrato', 'valor_pago', 'data_pagamento', 'forma', 'recibo')
        widgets = {
            'data_pagamento': DateInput(),
            'valor_pago': Numeros(),
        }

    def __init__(self, user, *args, **kwargs):
        super(FormPagamento, self).__init__(*args, **kwargs)
        self.fields['ao_contrato'].queryset = Contrato.objects.filter(do_locador=user)
        self.fields['valor_pago'].widget.attrs.update({'class': 'mask-valor'})


class FormGasto(ModelForm):
    class Meta:
        model = Gasto
        fields = ('do_imovel', 'valor', 'data', 'observacoes', 'comprovante')
        widgets = {
            'data': DateInput(),
            'valor': Numeros(),
        }

    def __init__(self, *args, **kwargs):
        super(FormGasto, self).__init__(*args, **kwargs)
        self.fields['valor'].widget.attrs['class'] = 'mask-valor'


class FormLocatario(forms.ModelForm):
    class Meta:
        model = Locatario
        fields = '__all__'
        exclude = ['do_locador', 'dataentrada']

    def __init__(self, *args, **kwargs):
        super(FormLocatario, self).__init__(*args, **kwargs)

        self.fields['CPF'].widget.attrs.update({'class': 'mask-cpf'})
        self.fields['telefone1'].widget.attrs.update({'class': 'mask-telefone1'})
        self.fields['telefone2'].widget.attrs.update({'class': 'mask-telefone2'})


class FormContrato(ModelForm):
    class Meta:
        model = Contrato
        exclude = ['do_locador', 'em_posse', 'rescindido', 'data_criacao', 'pagamentos_feitos']
        fields = ['do_locatario', 'do_imovel', 'data_entrada', 'data_saida', 'valor_mensal', 'dia_vencimento']
        widgets = {
            'data_entrada': DateInput(),
            'data_saida': DateInput(),
            'valor_mensal': Numeros(),
            'dia_vencimento': Numeros(),
        }

    def __init__(self, user, *args, **kwargs):
        super(FormContrato, self).__init__(*args, **kwargs)
        self.fields['do_locatario'].queryset = Locatario.objects.filter(do_locador=user)
        self.fields['do_imovel'].queryset = Imovei.objects.disponiveis().filter(do_locador=user)
        self.fields['valor_mensal'].widget.attrs.update({'class': 'mask-valor'})


class FormimovelGrupo(ModelForm):
    class Meta:
        model = ImovGrupo
        exclude = ['imoveis', 'do_usuario']
        fields = ['nome']
        labels = {
            "nome": ""}


class FormImovel(ModelForm):
    class Meta:
        model = Imovei
        exclude = ['do_locador', 'data_registro']
        fileds = ['nome', 'grupo', 'endereco', 'uc_energia', 'uc_agua']
        widgets = {
            'endereco': Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, user, *args, **kwargs):
        super(FormImovel, self).__init__(*args, **kwargs)
        self.fields['grupo'].queryset = ImovGrupo.objects.filter(do_usuario=user)


class FormAnotacoes(ModelForm):
    class Meta:
        model = Anotacoe
        exclude = ['do_locador']
        fields = ['titulo', 'data_registro', 'texto']
        widgets = {
            'data_registro': DateInput(),
            'texto': Textarea(),
        }
