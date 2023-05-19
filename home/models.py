import random, string
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from num2words import num2words

from Alugue_seu_imovel import settings
from django.db.models.aggregates import Sum
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator, MinValueValidator, \
    MaxValueValidator, FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.template.defaultfilters import date as data_ptbr
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import AbstractUser
from django_resized import ResizedImageField
from home.funcoes_proprias import valor_format, tratar_imagem, cpf_format, cel_format, cep_format
from ckeditor.fields import RichTextField
from home.funcoes_proprias import modelo_variaveis, modelo_condicoes

apenas_numeros = RegexValidator(regex=r'^[0-9]*$', message='Digite apenas números.')
estados_civis = (
    (0, 'Solteiro(a)'),
    (1, 'Casado(a)'),
    (2, 'Separado(a)'),
    (3, 'Divorciado(a)'),
    (4, 'Viuvo(a)'))


def user_uuid():
    con_codigo = ''.join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(10))
    return f'{con_codigo[:10]}'


def parcela_uuid():
    recibo_codigo = ''.join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in
        range(6))
    return f'{recibo_codigo[:3]}-{recibo_codigo[3:]}'


class Usuario(AbstractUser):
    RG = models.CharField(max_length=9, null=True, blank=True, help_text='Digite apenas números',
                          validators=[MinLengthValidator(7), MaxLengthValidator(9), apenas_numeros])
    CPF = models.CharField(max_length=11, null=True, blank=True, unique=True, help_text='Digite apenas números',
                           validators=[MinLengthValidator(11), MaxLengthValidator(11), apenas_numeros])
    telefone = models.CharField(max_length=11, null=False, blank=True, unique=True,
                                help_text='Celular/Digite apenas números',
                                validators=[MinLengthValidator(11), MaxLengthValidator(11), apenas_numeros])
    email = models.EmailField(unique=True)
    nacionalidade = models.CharField(null=True, blank=True, max_length=40, default='Brasileiro(a)')
    estadocivil = models.IntegerField(null=True, blank=True, verbose_name='Estado Civil', choices=estados_civis)
    ocupacao = models.CharField(null=True, blank=True, max_length=85, verbose_name='Ocupação')
    endereco_completo = models.CharField(null=True, blank=True, max_length=150, verbose_name='Endereço Completo')
    dados_pagamento1 = models.CharField(null=True, blank=True, max_length=90,
                                        verbose_name='Informações de pagamentos 1',
                                        help_text='Sua conta PIX ou dados bancários ou carteira crypto, etc...')
    dados_pagamento2 = models.CharField(null=True, blank=True, max_length=90,
                                        verbose_name='Informações de pagamentos 2')
    uuid = models.CharField(null=False, editable=False, max_length=10, unique=True, default=user_uuid)
    # outros poderão ter acesso ao uuid por cópias digitais de pdfs que poderão ser repassadas pelo usuario

    locat_slots = models.IntegerField(default=2)

    data_eventos_i = models.DateField(blank=True, null=True)
    itens_eventos = models.CharField(blank=True, null=True, max_length=31, default=['1', '2', '3', '4', '5', '6'])
    qtd_eventos = models.IntegerField(blank=True, null=True, default=10)
    ordem_eventos = models.IntegerField(default=1, blank=False)

    recibo_ultimo = models.ForeignKey('Contrato', null=True, blank=True, related_name='usuario_recibo_set',
                                      on_delete=models.SET_NULL)
    recibo_preenchimento = models.IntegerField(null=True, blank=True)

    tabela_ultima_data_ger = models.IntegerField(null=True, blank=True)
    tabela_meses_qtd = models.IntegerField(null=True, blank=True)
    tabela_imov_qtd = models.IntegerField(null=True, blank=True)

    contrato_ultimo = models.ForeignKey('Contrato', null=True, blank=True, related_name='usuario_contrato_set',
                                        on_delete=models.SET_NULL)

    def get_absolute_url(self):
        return reverse('home:Visão Geral', args=[str(self.pk, )])

    def nome_completo(self):
        return f'{str(self.first_name)} {str(self.last_name)}'

    def primeiro_ultimo_nome(self):
        nome = self.nome_completo().split()
        return f'{nome[0]} {nome[len(nome) - 1]}'

    def f_cpf(self):
        if self.CPF:
            return cpf_format(self.CPF)

    def f_tel(self):
        if self.telefone:
            return cel_format(self.telefone)


class LocatariosManager(models.Manager):
    def com_imoveis(self):
        return self.exclude(com_imoveis__isnull=True)

    def sem_imoveis(self):
        return self.exclude(com_imoveis__isnull=False)


class Locatario(models.Model):
    do_locador = models.ForeignKey('Usuario', null=True, blank=True, on_delete=models.CASCADE)
    com_imoveis = models.ManyToManyField('Imovei', blank=True)
    com_contratos = models.ManyToManyField('Contrato', blank=True)

    nome = models.CharField(max_length=100, blank=False, verbose_name='Nome Completo')
    docs = ResizedImageField(size=[1280, None], upload_to='locatarios_docs/%Y/%m/', blank=True,
                             verbose_name='Documentos', validators=[tratar_imagem, FileExtensionValidator])
    RG = models.CharField(max_length=9, null=False, blank=True, help_text='Digite apenas números',
                          validators=[MinLengthValidator(7), MaxLengthValidator(9), apenas_numeros])
    CPF = models.CharField(max_length=11, null=False, blank=False, help_text='Digite apenas números',
                           validators=[MinLengthValidator(11), MaxLengthValidator(11), apenas_numeros])
    ocupacao = models.CharField(max_length=85, verbose_name='Ocupação')
    endereco_completo = models.CharField(null=True, blank=True, max_length=150, verbose_name='Endereço Completo')
    telefone1 = models.CharField(max_length=11, blank=False, verbose_name='Telefone 1',
                                 help_text='Celular/Digite apenas números',
                                 validators=[MinLengthValidator(11), MaxLengthValidator(11), apenas_numeros])
    telefone2 = models.CharField(max_length=11, blank=True, verbose_name='Telefone 2',
                                 help_text='Celular/Digite apenas números',
                                 validators=[MinLengthValidator(11), MaxLengthValidator(11), apenas_numeros])
    email = models.EmailField(max_length=45, blank=True)
    nacionalidade = models.CharField(max_length=40, blank=False, default='Brasileiro(a)')
    estadocivil = models.IntegerField(blank=False, verbose_name='Estado Civil', choices=estados_civis)
    data_registro = models.DateTimeField(auto_now_add=True)
    objects = LocatariosManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["CPF", "do_locador"], name="cpf_locatario_por_usuario"),
        ]

    def get_absolute_url(self):
        return reverse('home:Locatários', args=[str(self.pk, )])

    def __str__(self):
        return f'{self.nome}'

    def primeiro_ultimo_nome(self):
        return f'{self.nome.split()[:1][0]} {self.nome.split()[len(self.nome.split()) - 1:][0]}'

    def imoveis_alugados(self):
        x = Imovei.objects.filter(com_locatario=self.pk)
        return x

    def f_cpf(self):
        if self.CPF:
            return cpf_format(self.CPF)

    def f_tel1(self):
        if self.telefone1:
            return cel_format(self.telefone1)

    def f_tel2(self):
        if self.telefone2:
            return cel_format(self.telefone2)
        # else:
        #     return ''

    def contratos_qtd(self):
        return Contrato.objects.filter(do_locatario=self).count()


tipos_de_imovel = (
    (0, 'Casa'),
    (1, 'Apartamento'),
    (2, 'Kitnet'),
    (3, 'Box/Loja'),
    (4, 'Escritório'),
    (5, 'Depósito/Armazém'),
    (6, 'Galpão'))


class ImovGrupo(models.Model):
    do_usuario = models.ForeignKey('Usuario', null=True, blank=True, on_delete=models.CASCADE)
    nome = models.CharField(max_length=35, blank=False, verbose_name='Criar Grupo')
    tipo = models.IntegerField(null=True, blank=True, choices=tipos_de_imovel, verbose_name='Tipo de Imóvel')
    imoveis = models.ManyToManyField('Imovei', blank=True)

    def get_absolute_url(self):
        return reverse('home:Criar Grupo Imóveis', args=[str(self.pk, )])

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ('nome',)


class ImoveiManager(models.Manager):
    def disponiveis(self):
        return self.filter(com_locatario=None)

    def ocupados(self):
        return self.exclude(com_locatario__isnull=True)


estados = (
    ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Ceará'),
    ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'), ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'),
    ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
    ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
    ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'), ('SP', 'São Paulo'),
    ('SE', 'Sergipe'), ('TO', 'Tocantins')
)


class Imovei(models.Model):
    do_locador = models.ForeignKey('Usuario', blank=False, on_delete=models.CASCADE)
    com_locatario = models.ForeignKey('Locatario', blank=True, null=True, on_delete=models.SET_NULL)
    contrato_atual = models.OneToOneField('Contrato', blank=True, null=True, on_delete=models.SET_NULL)
    grupo = models.ForeignKey('ImovGrupo', blank=True, null=True, on_delete=models.SET_NULL)

    nome = models.CharField(max_length=25, blank=False, verbose_name='Rótulo')
    cep = models.CharField(max_length=8, blank=False, verbose_name='CEP',
                           validators=[MinLengthValidator(8), MaxLengthValidator(8), apenas_numeros])
    endereco = models.CharField(max_length=150, blank=False, verbose_name='Endereço')
    numero = models.IntegerField(blank=False,
                                 validators=[MinValueValidator(1), MaxValueValidator(999999), apenas_numeros])
    complemento = models.CharField(max_length=80, blank=True)
    bairro = models.CharField(max_length=30, blank=False)
    cidade = models.CharField(max_length=30, blank=False)
    estado = models.CharField(max_length=2, blank=False, choices=estados)
    uc_energia = models.CharField(max_length=15, blank=True, verbose_name='Matrícula de Energia',
                                  validators=[MinLengthValidator(4), MaxLengthValidator(15)])
    uc_agua = models.CharField(max_length=15, blank=True, verbose_name='Matrícula de Saneamento',
                               validators=[MinLengthValidator(4), MaxLengthValidator(15)])
    data_registro = models.DateTimeField(default=datetime.now)
    objects = ImoveiManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["nome", "do_locador"], name="nome_imovel_por_usuario"),
        ]

    def __str__(self):
        return f'{self.nome} ({self.grupo})'

    # def get_absolute_url(self):
    #     return reverse('home:Imóveis', args=[str(self.pk), ])

    def nogrupo(self):
        return '' if self.grupo is None else self.grupo

    def esta_ocupado(self):
        return False if self.com_locatario is None else True

    def f_cep(self):
        return cep_format(self.cep)

    def endereco_base(self):
        return f'{self.endereco}, Nº{self.numero} ({self.complemento}) - {self.bairro}'

    def endereco_completo(self):
        return f'{self.endereco_base()} - {self.cidade}/{self.estado}, {self.f_cep()}'

    def receita_acumulada(self):
        parcelas = Parcela.objects.filter(do_imovel=self)
        total = 0
        for parcela in parcelas:
            total += int(parcela.tt_pago)
        return valor_format(str(total))


# Gerar o código para o contrato:
def gerar_codigo_contrato():
    codigos_existentes = list(Contrato.objects.all().values("codigo").values_list('codigo', flat=True))
    while True:
        con_codigo = ''.join(
            random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(10))
        if con_codigo not in codigos_existentes:
            return f'{con_codigo[:5]}-{con_codigo[5:]}'


class ContratoManager(models.Manager):
    def ativos(self):
        return self.filter(em_posse=True, rescindido=False, vencido=False)

    def inativos(self):
        return self.exclude(em_posse=True, rescindido=False, vencido=False)


class Contrato(models.Model):
    do_locador = models.ForeignKey('Usuario', null=True, blank=True, on_delete=models.CASCADE)
    do_locatario = models.ForeignKey('Locatario', on_delete=models.CASCADE,
                                     verbose_name='Locatário')
    do_imovel = models.ForeignKey('Imovei', on_delete=models.CASCADE, verbose_name='No imóvel')

    data_entrada = models.DateField(blank=False, verbose_name='Data de Entrada')
    duracao = models.IntegerField(null=False, blank=False, verbose_name='Duração do contrato(Meses)',
                                  validators=[MaxValueValidator(18), MinValueValidator(1)])
    valor_mensal = models.CharField(max_length=9, verbose_name='Valor Mensal (R$) ', blank=False,
                                    help_text='Digite apenas números',
                                    validators=[apenas_numeros, MinLengthValidator(3)])
    dia_vencimento = models.IntegerField(blank=False, validators=[MaxValueValidator(28), MinValueValidator(1)],
                                         verbose_name='Dia do vencimento', help_text='(1-28)')
    em_posse = models.BooleanField(default=False, null=False,
                                   help_text='Marque quando receber a sua via assinada e registrada em cartório')
    rescindido = models.BooleanField(default=False, null=False, help_text='Marque caso haja rescisão do contrato')
    vencido = models.BooleanField(default=False, null=False)
    codigo = models.CharField(null=False, editable=False, max_length=11, default=gerar_codigo_contrato)
    data_de_rescisao = models.DateField(blank=True, verbose_name='Data da rescisão', null=True)
    recibos_pdf = models.FileField(upload_to='recibos_docs/%Y/%m/', blank=True, verbose_name='Recibos')
    data_registro = models.DateTimeField(auto_now_add=True)
    objects = ContratoManager()

    def get_absolute_url(self):
        return reverse('home:Contratos', args=[str(self.pk), ])

    class Meta:
        ordering = ['-data_entrada']

    def nome_curto(self):
        return f'({self.do_locatario.primeiro_ultimo_nome()} - {self.data_entrada.strftime("%d/%m/%Y")} - ' \
               f'{self.codigo})'

    def __str__(self):
        return f'({self.do_locatario.primeiro_ultimo_nome()} - {self.do_imovel.nome} - ' \
               f'{self.data_entrada.strftime("%d/%m/%Y")})'

    def nome_completo(self):
        return f'{self.do_locatario.nome} - {self.do_imovel} - {self.data_entrada.strftime("%d/%m/%Y")} - ' \
               f'({self.codigo})'

    def valor_format(self):
        return valor_format(self.valor_mensal)

    def valor_por_extenso(self):
        reais = self.valor_mensal[:-2]
        centavos = self.valor_mensal[-2:]
        centavos_format = f' e {num2words(int(centavos), lang="pt_BR")} centavos'
        return f'{num2words(int(reais), lang="pt_BR").capitalize()} reais{centavos_format if int(centavos) > 1 else ""}'

    def valor_do_contrato(self):
        return str(int(self.valor_mensal) * int(self.duracao))

    def valor_do_contrato_format(self):
        return valor_format(self.valor_do_contrato())

    def valor_do_contrato_por_extenso(self):
        valor = str(int(self.valor_mensal) * int(self.duracao))
        reais = valor[:-2]
        centavos = valor[-2:]
        centavos_format = f' e {num2words(int(centavos), lang="pt_BR")} centavos'
        return f'{num2words(int(reais), lang="pt_BR").capitalize()} reais{centavos_format if int(centavos) > 1 else ""}'

    def total_quitado(self):
        valor = Parcela.objects.filter(do_contrato=self, tt_pago=self.valor_mensal).values_list('tt_pago')
        if settings.USAR_DB == 1:
            valor = valor.aggregate(Sum('tt_pago'))
            return valor['tt_pago__sum']
        elif settings.USAR_DB == 2 or settings.USAR_DB == 3:
            array = valor.aggregate(arr=ArrayAgg('tt_pago'))
            t = 0
            for _ in array['arr']:
                t += int(_)
            return t

    def total_pg_format(self):
        if self.total_quitado() is None:
            return 'R$0,00'
        else:
            return valor_format(str(self.total_quitado()))

    def falta_pg_format(self):
        if self.total_quitado() is None:
            return self.valor_do_contrato_format()
        else:
            return valor_format(str((int(self.valor_mensal) * int(self.duracao)) - self.total_quitado()))

    def em_maos(self):
        return 'Sim' if self.em_posse else 'Não'

    def data_saida(self):
        data = self.data_entrada + relativedelta(months=self.duracao)
        return data

    def ativo_hoje(self):
        return True if self.data_entrada <= datetime.today().date() <= self.data_saida() and self.em_posse is True \
                       and self.rescindido is False and self.vencido is False else False

    def ativo_futuramente(self):
        return True if self.data_entrada >= datetime.today().date() and self.rescindido is False else False

    def ativo_45_dias_atras(self):
        return True if self.data_saida() >= datetime.today().date() + timedelta(days=-45) else False

    def pagamento_total(self):
        pagamentos = Pagamento.objects.filter(ao_contrato=self.pk).values('valor_pago')
        valor_tt = 0
        for valor in pagamentos:
            valor_tt += int(valor['valor_pago'])
        return valor_tt

    def duracao_por_extenso(self):
        return num2words(self.duracao, lang='pt_BR')

    def dia_vencimento_por_extenso(self):
        return num2words(self.dia_vencimento, lang='pt_BR')

    def vencimento_atual(self):
        parcelas = Parcela.objects.filter(do_contrato=self, tt_pago__lt=self.valor_mensal)
        try:
            x = parcelas[0].data_pagm_ref
        except:
            x = None
        return x

    def vencimento_atual_textual(self):
        txt = ''
        try:
            if self.vencimento_atual() < datetime.today().date():
                txt = f'Venceu em {self.vencimento_atual().strftime("%d/%m/%Y")}'
            elif self.vencimento_atual() == datetime.today().date():
                txt = 'Vence Hoje'
            elif self.vencimento_atual() > datetime.today().date():
                txt = f'Vencerá em {self.vencimento_atual().strftime("%d/%m/%Y")}'
        except:
            txt = ''
        return txt

    def divida_atual_meses(self):
        parcelas_vencidas_n_pagas = Parcela.objects.filter(do_contrato=self, tt_pago__lt=self.valor_mensal,
                                                           data_pagm_ref__lte=datetime.today().date())
        return len(parcelas_vencidas_n_pagas)

    def divida_atual_valor(self):
        parcelas_vencidas_n_pagas = Parcela.objects.filter(do_contrato=self, tt_pago__lt=self.valor_mensal,
                                                           data_pagm_ref__lte=datetime.today().date())
        soma_tt_pg = parcelas_vencidas_n_pagas.aggregate(Sum('tt_pago'))['tt_pago__sum']
        valor = (len(parcelas_vencidas_n_pagas) * int(self.valor_mensal)) - (int(soma_tt_pg) if soma_tt_pg else 0)
        return valor, valor_format(str(valor))


class ContratoModelo(models.Model):
    titulo = models.CharField(blank=False, max_length=120, verbose_name='', help_text='Titulo')
    autor = models.ForeignKey('Usuario', blank=False, null=True, related_name='contratomod_autor_set',
                              on_delete=models.SET_NULL)
    corpo = RichTextField(null=True, blank=True, verbose_name='')
    data_criacao = models.DateTimeField(auto_now_add=True)
    variaveis = models.JSONField(null=True, blank=True)
    condicoes = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'{self.titulo}'

    def display_variaveis(self):
        variaveis = []
        for variavel in list(self.variaveis):
            if variavel in modelo_variaveis:
                variaveis.append([modelo_variaveis[variavel][0], modelo_variaveis[variavel][1]])
        return variaveis

    def display_condicoes(self):
        condicoes = []
        for condicao in list(self.condicoes):
            if condicao in modelo_condicoes:
                condicoes.append([modelo_condicoes[condicao][0], modelo_condicoes[condicao][1]])
        return condicoes


tipos_de_locacao = (
    (None, '-----------'),
    (1, 'residencial'),
    (2, 'não residencial'))


class ContratoDocConfig(models.Model):
    do_contrato = models.ForeignKey('Contrato', null=True, blank=False, on_delete=models.CASCADE)
    do_modelo = models.ForeignKey('ContratoModelo', null=True, blank=False, on_delete=models.SET_NULL,
                                  verbose_name='Modelo de contrato')

    tipo_de_locacao = models.IntegerField(null=True, blank=True, choices=tipos_de_locacao,
                                          verbose_name='Tipo de Locação')
    caucao = models.IntegerField(null=True, blank=True,
                                 validators=[MinValueValidator(0), MaxValueValidator(3), apenas_numeros])

    fiador_nome = models.CharField(max_length=100, null=True, blank=True, verbose_name='Nome Completo')
    fiador_RG = models.CharField(max_length=9, null=True, blank=True, help_text='Digite apenas números',
                                 validators=[MinLengthValidator(7), MaxLengthValidator(9), apenas_numeros],
                                 verbose_name='RG')
    fiador_CPF = models.CharField(max_length=11, null=True, blank=True, help_text='Digite apenas números',
                                  validators=[MinLengthValidator(11), MaxLengthValidator(11), apenas_numeros],
                                  verbose_name='CPF')
    fiador_ocupacao = models.CharField(max_length=85, null=True, blank=True, verbose_name='Ocupação')
    fiador_endereco_completo = models.CharField(null=True, blank=True, max_length=150, verbose_name='Endereço Completo')
    fiador_nacionalidade = models.CharField(max_length=40, null=True, blank=True, verbose_name='Nacionalidade')
    fiador_estadocivil = models.IntegerField(null=True, blank=True, verbose_name='Estado Civil', choices=estados_civis)

    def __str__(self):
        return f'{self.do_contrato} ({self.do_modelo})'

    def f_cpf(self):
        return cpf_format(self.fiador_CPF)


class Parcela(models.Model):
    do_usuario = models.ForeignKey('Usuario', blank=False, on_delete=models.CASCADE)
    do_contrato = models.ForeignKey('Contrato', null=False, blank=False, on_delete=models.CASCADE)
    do_imovel = models.ForeignKey('Imovei', null=False, blank=False, on_delete=models.CASCADE)
    do_locatario = models.ForeignKey('Locatario', null=False, blank=False, on_delete=models.CASCADE)
    da_tarefa = models.OneToOneField('Tarefa', null=True, on_delete=models.SET_NULL)
    codigo = models.CharField(blank=False, null=False, editable=False, max_length=7, unique_for_month=True,
                              default=parcela_uuid)
    data_pagm_ref = models.DateField(null=False, blank=False)
    tt_pago = models.CharField(max_length=9, blank=False, default=0)
    recibo_entregue = models.BooleanField(default=False)
    apagada = models.BooleanField(default=False)

    def __str__(self):
        return f'{str(self.do_imovel)[:8]} ({self.data_pagm_ref.strftime("%B/%Y")})'

    def tt_pago_format(self):
        return valor_format(self.tt_pago)

    def falta_pagar_format(self):
        contrato = Contrato.objects.get(pk=self.do_contrato.pk)
        return valor_format(str(int(contrato.valor_mensal) - int(self.tt_pago)))

    def esta_pago(self):
        contrato = Contrato.objects.get(pk=self.do_contrato.pk)
        return True if int(self.tt_pago) == int(contrato.valor_mensal) else False

    def esta_vencido(self):
        return True if datetime.today().date() > self.data_pagm_ref else False

    def posicao(self):
        try:
            parcelas = list(Parcela.objects.filter(do_contrato=self.do_contrato).values_list('pk', flat=True))
            parcela = self.pk
            return parcelas.index(parcela) + 1
        except:
            return None

    def definir_apagada(self):
        self.apagada = True
        self.save(update_fields=['apagada'])

    def restaurar(self):
        self.apagada = False
        self.save(update_fields=['apagada'])


lista_pagamentos = (
    (0, 'PIX'),
    (1, 'Din. Espécie'),
    (2, 'Boleto Banc.'),
    (3, 'Tranfer. Banc.'))


class Pagamento(models.Model):
    ao_locador = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    ao_contrato = models.ForeignKey('Contrato', on_delete=models.CASCADE,
                                    verbose_name='Do Contrato')
    do_locatario = models.ForeignKey('Locatario', on_delete=models.CASCADE)

    valor_pago = models.CharField(max_length=9, verbose_name='Valor Pago (R$) ', blank=False,
                                  validators=[apenas_numeros])
    data_pagamento = models.DateTimeField(blank=False, verbose_name='Data do Pagamento')
    data_de_recibo = models.DateTimeField(blank=True, verbose_name='Data em que foi marcado recibo entregue', null=True)
    forma = models.IntegerField(blank=False, choices=lista_pagamentos, verbose_name='Forma de Pagamento')
    data_criacao = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('home:Pagamentos', args=[(str(self.pk)), ])

    def valor_format(self):
        return valor_format(self.valor_pago)

    def __str__(self):
        return f'{self.do_locatario} - R${self.valor_format()} - {self.data_pagamento.strftime("%D")}'


class Gasto(models.Model):
    do_locador = models.ForeignKey('Usuario', null=False, on_delete=models.CASCADE)
    do_imovel = models.ForeignKey('Imovei', blank=True, null=True, on_delete=models.CASCADE,
                                  help_text='Deixe em branco para registrar um gasto geral')

    valor = models.CharField(max_length=9, verbose_name='Valor Gasto (R$) ', blank=False, validators=[apenas_numeros])
    data = models.DateTimeField(blank=False)
    observacoes = models.TextField(max_length=500, blank=True, verbose_name='Observações')
    comprovante = ResizedImageField(size=[1280, None], upload_to='gastos_comprovantes/%Y/%m/', blank=True,
                                    verbose_name='Comporvante', validators=[tratar_imagem, FileExtensionValidator])
    data_criacao = models.DateTimeField(auto_now_add=True)

    def get_alsolute_url(self):
        return reverse('home:Gastos', args=[(str(self.pk)), ])

    def valor_format(self):
        return valor_format(self.valor)

    def __str__(self):
        return f'{self.observacoes[:20]} - {self.valor_format()} - {self.data.strftime("%D")}'


class Anotacoe(models.Model):
    do_usuario = models.ForeignKey('Usuario', null=False, on_delete=models.CASCADE)
    da_tarefa = models.OneToOneField('Tarefa', null=True, blank=True, on_delete=models.SET_NULL)

    titulo = models.CharField(blank=False, max_length=100, verbose_name='Título')
    data_registro = models.DateTimeField(blank=True)
    texto = models.TextField(blank=True, null=True)
    tarefa = models.BooleanField(default=False,
                                 help_text='Marque para adicionar este registro na sua lista de tarefas.')
    feito = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('home:Anotações', args=[(str(self.pk)), ])

    def tipo(self):
        if self.tarefa:
            if self.feito:
                return 'Tarefa concluída'
            else:
                return 'Tarefa pendente'
        else:
            return 'Anotação'

    def __str__(self):
        return f'{self.titulo} - {self.data_registro.strftime("%d/%m/%Y")}'

    def texto_pequeno(self):
        tamanho = 50
        if len(self.texto) == 0:
            return [0, '---']
        elif len(self.texto) < tamanho:
            return [1, self.texto]
        else:
            return [2, f'{self.texto[:tamanho]}...']


class Tarefa(models.Model):
    do_usuario = models.ForeignKey('Usuario', null=False, on_delete=models.CASCADE)
    autor_classe = models.ForeignKey(ContentType, null=False, on_delete=models.CASCADE)
    objeto_id = models.PositiveIntegerField(null=False)
    content_object = GenericForeignKey('autor_classe', 'objeto_id')

    data_registro = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)
    apagada = models.BooleanField(default=False)
    # \/ extinguir este campo, já que estes dados serão salvos nos objetos autores desta tarefa, não mais aqui nela
    # agora que o acesso a elas fica fácil através dos objetos autores(one_to_one_field/content_object)
    dados = models.JSONField(null=True, blank=True)
    data_lida = models.DateTimeField(null=True)

    def __str__(self):
        return f'Tarefa: classe:{self.autor_classe}/objeto_id:{self.objeto_id}'

    class Meta:
        ordering = ['-data_registro']

    def autor_tipo(self):
        if self.autor_classe == ContentType.objects.get_for_model(Parcela):
            return 1
        elif self.autor_classe == ContentType.objects.get_for_model(Anotacoe):
            return 2

    def autor_tipo_display(self):
        if self.autor_classe == ContentType.objects.get_for_model(Parcela):
            return '🧾Recibo'
        elif self.autor_classe == ContentType.objects.get_for_model(Anotacoe):
            return '🗒️Tarefa'

    def recibo_entregue(self):
        if self.dados['recibo_entregue']:
            return self.dados['recibo_entregue']
        else:
            return False

    def definir_apagada(self):
        self.apagada = True
        self.save(update_fields=['apagada'])

    def restaurar(self):
        self.apagada = False
        self.save(update_fields=['apagada'])

    def afazer_concluida(self):
        if self.dados['afazer_concluida']:
            if self.dados['afazer_concluida'] == 2:
                return True
            elif self.dados['afazer_concluida'] == 3:
                return False
        else:
            return 1

    def borda(self):
        if self.autor_classe == ContentType.objects.get_for_model(Parcela):
            return 'border-white'
        elif self.autor_classe == ContentType.objects.get_for_model(Anotacoe):
            return 'border-warning'

    def texto(self):
        mensagem = ''
        if self.autor_classe == ContentType.objects.get_for_model(Parcela):
            try:
                parcela = self.content_object
                mensagem = f'O Pagamento de {parcela.do_contrato.do_locatario.primeiro_ultimo_nome().upper()}' \
                           f' referente à parcela de {data_ptbr(parcela.data_pagm_ref, "F/Y").upper()}' \
                           f'(Parcela {parcela.posicao()} de {parcela.do_contrato.duracao}) do contrato ' \
                           f'{parcela.do_contrato.codigo} foi detectado. Confirme a entrega do recibo.'
            except:
                pass
        elif self.autor_classe == ContentType.objects.get_for_model(Anotacoe):
            try:
                nota = self.content_object
                mensagem = f'{nota.titulo}{nota.texto}'
            except:
                pass
        return mensagem


lista_mensagem = (
    (1, 'Elogio'),
    (2, 'Reclamação'),
    (3, 'Dúvida'),
    (4, 'Report de bug'))


class DevMensagen(models.Model):
    do_usuario = models.ForeignKey('Usuario', null=True, blank=True, on_delete=models.CASCADE)

    data_registro = models.DateTimeField(auto_now=True)
    titulo = models.CharField(blank=False, max_length=100)
    mensagem = models.TextField(blank=False)
    tipo_msg = models.IntegerField(blank=False, choices=lista_mensagem)
    imagem = ResizedImageField(size=[1280, None], upload_to='mensagens_ao_dev/%Y/%m/', blank=True,
                               validators=[tratar_imagem, FileExtensionValidator])

    def get_absolute_url(self):
        return reverse('home:Mensagem pro Desenvolvedor', args=[(str(self.pk)), ])

    def __str__(self):
        return f'{self.do_usuario} - {self.titulo} - {self.data_registro}'


class Sugestao(models.Model):
    do_usuario = models.ForeignKey('Usuario', null=True, blank=True, on_delete=models.CASCADE)

    data_registro = models.DateTimeField(auto_now=True)
    corpo = models.TextField(max_length=1500, blank=False, null=False, verbose_name='')
    imagem = ResizedImageField(size=[1280, None], upload_to='sugestoes_docs/%Y/%m/', blank=True,
                               validators=[tratar_imagem, FileExtensionValidator], verbose_name='Imagem(opcional)')
    likes = models.ManyToManyField('Usuario', related_name='Likes', blank=True)
    implementada = models.BooleanField(default=False)
    aprovada = models.BooleanField(default=False)
    data_implementada = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Sugestões'

    def numero_de_likes(self):
        return self.likes.count()

    def __str__(self):
        return f'{self.do_usuario} - {self.corpo[:30]} - {self.data_registro}'
