import random, string, json
from datetime import datetime

from dateutil.relativedelta import relativedelta

from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django_resized import ResizedImageField
from home.funcoes_proprias import valor_format, tratar_imagem, cpf_format, cel_format, cep_format

apenas_numeros = RegexValidator(regex=r'^[0-9]*$', message='Digite apenas números.')


def user_uuid():
    con_codigo = ''.join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(10))
    return f'{con_codigo[:10]}'


class Usuario(AbstractUser):
    RG = models.CharField(max_length=9, null=True, blank=True, help_text='Digite apenas números',
                          validators=[MinLengthValidator(7), MaxLengthValidator(9), apenas_numeros])
    CPF = models.CharField(max_length=11, null=True, blank=True, help_text='Digite apenas números',
                           validators=[MinLengthValidator(11), MaxLengthValidator(11), apenas_numeros])
    telefone = models.CharField(max_length=11, null=False, blank=True, help_text='Digite apenas números',
                                validators=[apenas_numeros])
    uuid = models.CharField(null=False, editable=False, max_length=10, unique=True, default=user_uuid)

    locat_slots = models.IntegerField(default=2)

    data_eventos_i = models.DateField(blank=True, null=True)
    itens_eventos = models.CharField(blank=True, null=True, max_length=31, default=['1', '2', '3', '4', '5', '6'])
    qtd_eventos = models.IntegerField(blank=True, null=True, default=10)
    ordem_eventos = models.IntegerField(default=1, blank=False)

    recibo_ultimo = models.ForeignKey('Contrato', null=True, blank=True, on_delete=models.SET_NULL)
    recibo_preenchimento = models.IntegerField(null=True, blank=True)

    tabela_ultima_data_ger = models.IntegerField(null=True, blank=True)
    tabela_meses_qtd = models.IntegerField(null=True, blank=True)
    tabela_imov_qtd = models.IntegerField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse('home:DashBoard', args=[str(self.pk, )])

    def nome_completo(self):
        return f'{str(self.first_name)} {str(self.last_name)}'

    def primeiro_ultimo_nome(self):
        nome = self.nome_completo().split()
        return f'{nome[0]} {nome[len(nome) - 1]}'


estados_civis = (
    (0, 'Solteiro(a)'),
    (1, 'Casado(a)'),
    (2, 'Separado(a)'),
    (3, 'Divorciado(a)'),
    (4, 'Viuvo(a)'))


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
                             verbose_name='Documentos', validators=[tratar_imagem])
    RG = models.CharField(max_length=9, null=False, blank=True, help_text='Digite apenas números',
                          validators=[MinLengthValidator(7), MaxLengthValidator(9), apenas_numeros])
    CPF = models.CharField(max_length=11, null=False, blank=False, help_text='Digite apenas números',
                           validators=[MinLengthValidator(11), MaxLengthValidator(11), apenas_numeros])
    ocupacao = models.CharField(max_length=85, verbose_name='Ocupação')
    telefone1 = models.CharField(max_length=11, blank=False, verbose_name='Telefone 1',
                                 help_text='Digite apenas números',
                                 validators=[MinLengthValidator(11), MaxLengthValidator(11), apenas_numeros])
    telefone2 = models.CharField(max_length=11, blank=True, verbose_name='Telefone 2',
                                 help_text='Digite apenas números',
                                 validators=[MinLengthValidator(11), MaxLengthValidator(11), apenas_numeros])
    email = models.EmailField(max_length=45, blank=True)
    nacionalidade = models.CharField(max_length=40, blank=False, default='Brasileiro(a)')
    estadocivil = models.IntegerField(blank=False, verbose_name='Estado Civil', choices=estados_civis)
    data_registro = models.DateTimeField(auto_now_add=True)
    objects = LocatariosManager()

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
        return cpf_format(self.CPF)

    def f_tel1(self):
        return cel_format(self.telefone1)

    def f_tel2(self):
        return cel_format(self.telefone2)


class ImovGrupo(models.Model):
    do_usuario = models.ForeignKey('Usuario', null=True, blank=True,
                                   on_delete=models.CASCADE)

    nome = models.CharField(max_length=35, blank=False, verbose_name='Criar Grupo')
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

    def __str__(self):
        return f'{self.nome} ({self.grupo})'

    def get_absolute_url(self):
        return reverse('home:Imóveis', args=[str(self.pk), ])

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


# Gerar o codigo para o contrato:
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
    valor_mensal = models.CharField(max_length=9, verbose_name='Valor Mensal (R$): ', blank=False,
                                    help_text='Digite apenas números', validators=[apenas_numeros])
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

    def valor_do_contrato(self):
        return valor_format(str(int(self.valor_mensal) * int(self.duracao)))

    def total_quitado(self):
        pass

    def faltando_p_quitar(self):
        pass

    def em_maos(self):
        return 'Sim' if self.em_posse else 'Não'

    def data_saida(self):
        data = self.data_entrada + relativedelta(months=self.duracao)
        return data

    def ativo_hoje(self):
        return True if self.data_entrada <= datetime.today().date() <= self.data_saida() and self.em_posse is True \
                       and self.rescindido is False and self.vencido is False else False

    def pagamento_total(self):
        pagamentos = Pagamento.objects.filter(ao_contrato=self.pk).values('valor_pago')
        valor_tt = 0
        for valor in pagamentos:
            valor_tt += int(valor['valor_pago'])
        return valor_tt


class Parcela(models.Model):
    do_usuario = models.ForeignKey('Usuario', blank=False, on_delete=models.CASCADE)
    do_contrato = models.ForeignKey('Contrato', null=False, blank=False, on_delete=models.CASCADE)
    do_imovel = models.ForeignKey('Imovei', null=False, blank=False, on_delete=models.CASCADE)
    do_locatario = models.ForeignKey('Locatario', null=False, blank=False, on_delete=models.CASCADE)

    codigo = models.CharField(blank=False, null=False, editable=False, max_length=11)
    data_pagm_ref = models.DateField(null=False, blank=False)
    tt_pago = models.CharField(max_length=9, blank=False, default=0)
    recibo_entregue = models.BooleanField(default=False)

    def __str__(self):
        return f'{str(self.do_imovel)[:8]} ({self.data_pagm_ref.strftime("%B/%Y")})'

    def tt_pago_format(self):
        return valor_format(self.tt_pago)

    def falta_pagar_format(self):
        contrato = Contrato.objects.get(pk=self.do_contrato.pk)
        return valor_format(str(int(contrato.valor_mensal) - int(self.tt_pago)))

    def esta_pago(self):
        contrato = Contrato.objects.get(pk=self.do_contrato.pk)
        return True if self.tt_pago == contrato.valor_mensal else False

    def esta_vencido(self):
        return True if datetime.today().date() > self.data_pagm_ref else False


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

    valor_pago = models.CharField(max_length=9, verbose_name='Valor Pago (R$): ', blank=False,
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
    do_imovel = models.ForeignKey('Imovei', blank=False, on_delete=models.CASCADE)

    valor = models.CharField(max_length=9, verbose_name='Valor Gasto (R$): ', blank=False, validators=[apenas_numeros])
    data = models.DateTimeField(blank=False)
    observacoes = models.TextField(max_length=500, blank=True, verbose_name='Observações')
    comprovante = ResizedImageField(size=[1280, None], upload_to='gastos_comprovantes/%Y/%m/', blank=True,
                                    verbose_name='Comporvante', validators=[tratar_imagem])
    data_criacao = models.DateTimeField(auto_now_add=True)

    def get_alsolute_url(self):
        return reverse('home:Gastos', args=[(str(self.pk)), ])

    def valor_format(self):
        return valor_format(self.valor)

    def __str__(self):
        return f'{self.observacoes[:20]} - {self.valor_format()} - {self.data.strftime("%D")}'


class Anotacoe(models.Model):
    do_usuario = models.ForeignKey('Usuario', null=False, on_delete=models.CASCADE)

    titulo = models.CharField(blank=False, max_length=100, verbose_name='Título')
    data_registro = models.DateTimeField(blank=True)
    texto = models.TextField(blank=True, null=True)
    feito = models.IntegerField(choices=[(1, 'Anotação'), (2, 'Tarefa'), (3, 'Tarefa Concluida')], default=1)

    def get_absolute_url(self):
        return reverse('home:Anotações', args=[(str(self.pk)), ])

    def __str__(self):
        return f'{self.titulo} - {self.data_registro.strftime("%d/%m/%Y")}'

    def tarefa_afazer_concluida(self):
        if self.feito == 1:
            return 'Anotação'
        elif self.feito == 2:
            return 'Tarefa afazer'
        else:
            return 'Tarefa concluida'


tipos = [(1, '🧾Recibo'), (2, '🗒️Tarefa')]


class Tarefa(models.Model):
    do_usuario = models.ForeignKey('Usuario', null=False, on_delete=models.CASCADE)
    autor_id = models.IntegerField()
    autor_tipo = models.IntegerField(choices=tipos)
    texto = models.TextField(blank=False)
    data_registro = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)
    dados = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'{self.pk} - {self.texto[:15]}'

    class Meta:
        ordering = ['-data_registro']

    def recibo_entregue(self):
        if self.dados['recibo_entregue']:
            return self.dados['recibo_entregue']
        else:
            print('Esta tarefa não possui o dado "recibo_entregue"')
            return False

    def afazer_concluida(self):
        if self.dados['afazer_concluida']:
            if self.dados['afazer_concluida'] == 2:
                return True
            elif self.dados['afazer_concluida'] == 3:
                return False
        else:
            print('Esta tarefa não possui o dado "afazer_concluida"')
            return 1

    def borda(self):
        if self.autor_tipo == 1:
            return 'border-white'
        elif self.autor_tipo == 2:
            return 'border-warning'


lista_mensagem = (
    (1, 'Elogio'),
    (2, 'Reclamação'),
    (3, 'Dúvida'),
    (4, 'Sujestão'),
    (5, 'Report de bug'))


class MensagemDev(models.Model):
    do_usuario = models.ForeignKey('Usuario', null=True, blank=True,
                                   on_delete=models.CASCADE)

    data_registro = models.DateTimeField(auto_now=True)
    titulo = models.CharField(blank=False, max_length=100)
    mensagem = models.TextField(blank=False)
    tipo_msg = models.IntegerField(blank=False, choices=lista_mensagem)
    imagem = ResizedImageField(size=[1280, None], upload_to='mensagens_ao_dev/%Y/%m/', blank=True,
                               validators=[tratar_imagem])

    def get_absolute_url(self):
        return reverse('home:Mensagem pro Desenvolvedor', args=[(str(self.pk)), ])

    def __str__(self):
        return f'{self.do_usuario} - {self.titulo} - {self.data}'
