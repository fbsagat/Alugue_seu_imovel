from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from Alugue_seu_imovel import settings
from home.funcoes_proprias import valor_format

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from crispy_forms.bootstrap import InlineCheckboxes
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout

from home.models import Usuario, DevMensagen, Pagamento, Gasto, Locatario, Contrato, Imovei, Anotacoe, ImovGrupo, \
    ContratoDocConfig, ContratoModelo, Sugestao


class Textarea(forms.Textarea):
    input_type = 'text'


class DateInput(forms.DateInput):
    input_type = 'date'


class Numeros(forms.NumberInput):
    input_type = 'numbers'


class FormCriarConta(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'telefone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(FormCriarConta, self).__init__(*args, **kwargs)
        self.fields['telefone'].widget.attrs['class'] = 'mask-telefone1'


class FormUsuario(UserChangeForm):
    class Meta:
        model = Usuario
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'telefone', 'RG', 'CPF', 'nacionalidade',
                  'estadocivil', 'ocupacao', 'endereco_completo', 'dados_pagamento1', 'dados_pagamento2']

    def __init__(self, *args, **kwargs):
        super(FormUsuario, self).__init__(*args, **kwargs)
        self.fields['dados_pagamento1'].widget.attrs['class'] = 'form-control-sm'
        self.fields['dados_pagamento2'].widget.attrs['class'] = 'form-control-sm'


class FormEventos(forms.Form):
    mostrar_em_eventos = [
        (1, 'Pagamentos'),
        (2, 'Gastos'),
        (3, 'Locatarios'),
        (4, 'Contratos'),
        (5, 'Imóveis'),
        (6, 'Anotações'),
    ]

    ordem_em_eventos = [
        (1, 'Recentes'),
        (2, 'Antigos'),
    ]

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


class FormHomePage(forms.Form):
    email = forms.EmailField(label=False)


class FormMensagem(forms.ModelForm):
    class Meta:
        model = DevMensagen
        fields = '__all__'
        exclude = ['do_usuario', 'data_criacao']
        widgets = {
            'mensagem': Textarea(),
        }


class FormSugestao(forms.ModelForm):
    class Meta:
        model = Sugestao
        fields = '__all__'
        exclude = ['do_usuario', 'data_registro', 'implementada', 'likes']

        widgets = {
            'corpo': Textarea(attrs={'cols': 500, 'rows': 22}),

        }


class Mascara(forms.ModelForm):
    class Media:
        js = ('js/jquery.mask.min.js', 'js/custom.js')

    def __init__(self, *args, **kwargs):
        super(Mascara, self).__init__(*args, **kwargs)
        self.fields['telefone1'].widget.attrs['class'] = 'mask-telefone1'
        self.fields['telefone2'].widget.attrs['class'] = 'mask-telefone2'
        self.fields['CPF'].widget.attrs['class'] = 'mask-cpf'


class FormPagamento(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = '__all__'
        exclude = ['ao_locador', 'do_locatario', 'data_de_recibo', 'data_criacao']
        widgets = {
            'data_pagamento': DateInput(),
            'valor_pago': Numeros(),
        }

    def clean_valor_pago(self):
        valor_pago = self.cleaned_data['valor_pago']
        ao_contrato = self.cleaned_data['ao_contrato']
        contrato = Contrato.objects.get(pk=ao_contrato.pk)
        pagamento_tt = contrato.pagamento_total()
        total = int(contrato.valor_mensal) * int(contrato.duracao)
        total_futuro = pagamento_tt + int(valor_pago)
        valor_maximo = total - pagamento_tt
        if total_futuro > total:
            raise forms.ValidationError(
                f"Com este valor o limite total do contrato será ultrapassado. Valor máximo: "
                f"{valor_format(str(total - pagamento_tt))}" if valor_maximo > 0 else
                f'Impossível adicionar mais pagamentos, o contrato está quitado.'
                f' Valor total: {valor_format(str(total))}.')
        else:
            return valor_pago

    def __init__(self, user, *args, **kwargs):
        super(FormPagamento, self).__init__(*args, **kwargs)
        self.fields['ao_contrato'].queryset = Contrato.objects.filter(do_locador=user)
        self.fields['valor_pago'].widget.attrs.update({'class': 'mask-valor'})


class FormGasto(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = '__all__'
        exclude = ['do_locador', 'data_criacao']
        widgets = {
            'observacoes': Textarea(attrs={'cols': 100, 'rows': 12}),
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
        exclude = ['do_locador', 'com_imoveis', 'com_contratos', 'data_registro']

    def __init__(self, *args, usuario, **kwargs):
        super(FormLocatario, self).__init__(*args, **kwargs)
        self.fields['CPF'].widget.attrs.update({'class': 'mask-cpf'})
        self.fields['telefone1'].widget.attrs.update({'class': 'mask-telefone1'})
        self.fields['telefone2'].widget.attrs.update({'class': 'mask-telefone2'})
        self.locador_pk = usuario

    def clean_CPF(self):
        cpf = self.cleaned_data['CPF']
        cpfs_dos_locat_deste_user = Locatario.objects.filter(do_locador=self.locador_pk).exclude(
            pk=self.instance.pk).values_list('CPF', flat=True)
        if cpf in cpfs_dos_locat_deste_user:
            raise forms.ValidationError("Já existe um locatário registrado com este CPF.")
        else:
            return cpf


class FormContrato(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = '__all__'
        exclude = ['do_locador', 'em_posse', 'rescindido', 'vencido', 'codigo', 'data_de_rescisao', 'recibos_pdf',
                   'data_registro']
        widgets = {
            'data_entrada': DateInput(),
            'duracao': Numeros(),
            'valor_mensal': Numeros(),
            'dia_vencimento': Numeros(),
        }

    # ATENÇÃO VERIFICAR SE ISSO AQUI AINDA É ÚTIL OU DEIXEI LIXO PRA TRÁS \/
    # def __init__(self, property_id, *args, **kwargs):
    #     self.property_id = property_id
    #     super(FormContrato, self).__init__(*args, **kwargs)

    def clean_data_entrada(self):
        entrada = self.cleaned_data['data_entrada']
        duracao = int(self.data['duracao'])
        saida = entrada + relativedelta(months=duracao)
        imovel = self.cleaned_data['do_imovel']

        contratos_deste_imovel = Contrato.objects.filter(do_imovel=imovel.pk).exclude(pk=self.instance.pk)
        permitido = True

        # Se a data de entrada(data_entrada) estiver entre as datas de
        # entrada e de saida de cada contrato existente para este imovel, raise error
        for contrato in contratos_deste_imovel:
            data_in_out = {'entrada': contrato.data_entrada,
                           'saida': contrato.data_entrada + relativedelta(months=contrato.duracao)}

            if data_in_out['entrada'] <= entrada <= data_in_out['saida']:
                permitido = False
            if data_in_out['entrada'] <= saida <= data_in_out['saida']:
                permitido = False
        if permitido is False:
            raise forms.ValidationError("Já existe um contrato registrado para este imóvel neste período.")
        else:
            return entrada

    def __init__(self, user, *args, **kwargs):
        super(FormContrato, self).__init__(*args, **kwargs)
        self.fields['do_locatario'].queryset = Locatario.objects.filter(do_locador=user)
        self.fields['do_imovel'].queryset = Imovei.objects.filter(do_locador=user)
        self.fields['valor_mensal'].widget.attrs.update({'class': 'mask-valor'})


class FormContratoDoc(forms.Form):
    contrato = forms.ModelChoiceField(label='', queryset=Contrato.objects.none(), initial='')

    def __init__(self, *args, **kwargs):
        super(FormContratoDoc, self).__init__(*args, **kwargs)
        self.fields['contrato'].widget.attrs.update({'class': 'mt-3'})


class FormContratoDocConfig(forms.ModelForm):
    caucao = forms.IntegerField(help_text='Multiplicado pelo valor de uma parcela', label='Caução (parcela multipl.)',
                                max_value=3, min_value=0, initial=1, required=False)

    class Meta:
        model = ContratoDocConfig
        fields = '__all__'
        exclude = ['do_contrato']

    def __init__(self, *args, **kwargs):
        super(FormContratoDocConfig, self).__init__(*args, **kwargs)
        self.fields['fiador_CPF'].widget.attrs['id'] = 'id_CPF'
        self.fields['tipo_de_locacao'].choices = ((None, '-----------'), (1, 'Residencial'), (2, 'Não residencial'))

    def clean(self):
        msg = 'Para fiador este campo deve ser preenchido'
        cleaned_data = super(FormContratoDocConfig, self).clean()
        fiador_nome = cleaned_data.get("fiador_nome")
        fiador_cpf = cleaned_data.get("fiador_CPF")

        if fiador_nome and fiador_cpf is None:
            self.add_error('fiador_CPF', msg)

        elif fiador_cpf and fiador_nome is None:
            self.add_error('fiador_nome', msg)
        return cleaned_data


class FormContratoModelo(forms.ModelForm):
    class Meta:
        model = ContratoModelo
        fields = '__all__'
        exclude = ['autor', 'data_criacao', 'variaveis', 'condicoes']

    def __init__(self, *args, **kwargs):
        super(FormContratoModelo, self).__init__(*args, **kwargs)
        self.fields['titulo'].widget.attrs.update({'class': 'text-center'})


class FormimovelGrupo(forms.ModelForm):
    class Meta:
        model = ImovGrupo
        fields = '__all__'
        exclude = ['imoveis', 'do_usuario']
        labels = {
            "nome": ""}


class FormImovel(forms.ModelForm):
    class Meta:
        model = Imovei
        fileds = '__all__'
        exclude = ['do_locador', 'com_locatario', 'contrato_atual', 'data_registro']

    def __init__(self, user, *args, **kwargs):
        super(FormImovel, self).__init__(*args, **kwargs)
        self.fields['grupo'].queryset = ImovGrupo.objects.filter(do_usuario=user)
        self.fields['cep'].widget.attrs.update({'class': 'mask-cep'})
        self.fields['cep'].widget.attrs.update({'id': 'id_CEP'})
        self.user = user

    def clean_nome(self):
        nome = self.cleaned_data['nome']
        nomes_dos_imoveis_deste_user = Imovei.objects.filter(do_locador=self.user).exclude(
            pk=self.instance.pk).values_list('nome', flat=True)
        if nome in nomes_dos_imoveis_deste_user:
            raise forms.ValidationError("Já existe um Imóvel registrado com este rótulo.")
        else:
            return nome

    # Forma clean do campo unico
    def clean_uc_energia(self):
        uc_energia = self.cleaned_data['uc_energia']
        uc_energia_dos_imoveis_deste_user = Imovei.objects.filter(do_locador=self.user).exclude(
            pk=self.instance.pk).values_list('uc_energia',
                                             flat=True)
        if uc_energia in uc_energia_dos_imoveis_deste_user:
            raise forms.ValidationError("Já existe um Imóvel registrado com esta matrícula de Energia.")
        else:
            return uc_energia

    def clean_uc_agua(self):
        uc_agua = self.cleaned_data['uc_agua']
        uc_agua_dos_imoveis_deste_user = Imovei.objects.filter(do_locador=self.user).exclude(
            pk=self.instance.pk).values_list('uc_agua',
                                             flat=True)
        if uc_agua in uc_agua_dos_imoveis_deste_user:
            raise forms.ValidationError("Já existe um Imóvel registrado com esta matrícula de Energia.")
        else:
            return uc_agua


class FormAnotacoes(forms.ModelForm):

    class Meta:
        model = Anotacoe
        fields = '__all__'
        exclude = ['do_usuario', 'feito']
        widgets = {
            'data_registro': DateInput(attrs={'style': 'width: 140px;'}),
            'texto': Textarea(attrs={'cols': 10, 'rows': 15}),
        }


class FormRecibos(forms.Form):
    data_pre = [(1, '___/___/___'), (2, '___/mês/ano'), (3, 'dia/mês/ano')]
    contrato = forms.ModelChoiceField(label='', queryset=Contrato.objects.none(), initial='')
    data_preenchimento = forms.ChoiceField(label='', choices=data_pre, required=True)

    def __init__(self, *args, **kwargs):
        # user = kwargs.pop('user', None) # Acho q não é util
        super(FormRecibos, self).__init__(*args, **kwargs)
        self.fields['contrato'].widget.attrs['class'] = 'form-select form-select-sm'
        self.fields['data_preenchimento'].widget.attrs['class'] = 'form-select form-select-sm'


class FormTabela(forms.Form):
    meses = [(0, '...'), (1, '...'), (2, '...'), (3, '...'), (4, '...'), (5, '...'), (6, '...')]
    mostrar = [(4, '4'), (5, '5'), (6, '6'), (7, '7')]
    itens = [(6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10')]

    mes = forms.ChoiceField(label='', initial='', choices=meses, required=True)
    mostrar_qtd = forms.ChoiceField(label='', initial=7, choices=mostrar, required=True)
    itens_qtd = forms.ChoiceField(label='', initial=10, choices=itens, required=True)


class FormAdmin(forms.Form):
    escolhas = (
        ('1', f'Criar {settings.FICT_QTD["locatario"]} Locatários'),
        ('2', f'Criar {settings.FICT_QTD["imovel"]} Imoveis'),
        ('3', f'Criar {settings.FICT_QTD["contrato"]} Contratos'),
        ('4', f'Criar {settings.FICT_QTD["pagamento"]} Pagamentos'),
        ('5', f'Criar {settings.FICT_QTD["gasto"]} Gastos'),
        ('6', f'Criar {settings.FICT_QTD["nota"]} Anotações'),
        ('7', f'Criar {settings.FICT_QTD["sugestoes"]} Sugestões'),
        ('1000', '-------------'),
        ('100', f'Criar todos acima'),
        ('1000', '-------------'),
        ('150', f'Criar {settings.FICT_QTD["user"]} Usuários'),
        ('160', f'Criar {settings.FICT_QTD["imovel_g"]} Imov_Grupos'),
        ('170', 'Teste Mensagem'),
    )

    executar = forms.ChoiceField(choices=escolhas, initial='100')
    p_usuario = forms.ModelChoiceField(label='', queryset=Usuario.objects.all(), initial='')
    multiplicar_por = forms.IntegerField(max_value=10, min_value=0, initial=1)

    def __init__(self, *args, **kwargs):
        super(FormAdmin, self).__init__(*args, **kwargs)
        self.fields['multiplicar_por'].widget.attrs.update(style="width: 60px;")
        self.fields['executar'].widget.attrs['class'] = 'mt-1 form-control form-control-sm'
        self.fields['p_usuario'].widget.attrs['class'] = 'mt-1 form-control form-control-sm'
        self.fields['multiplicar_por'].widget.attrs['class'] = 'mt-1 form-control form-control-sm'
