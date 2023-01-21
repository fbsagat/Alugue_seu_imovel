from django.db import models
from datetime import datetime
from django.db.models.constraints import CheckConstraint
from django.db.models import Q, F
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from home.funcoes_proprias import valor_br


class Usuario(AbstractUser):
    locatarios = models.ManyToManyField('Locatario', blank=True)
    imoveis = models.ManyToManyField('Imovei', blank=True)
    contratos = models.ManyToManyField('Contrato', blank=True)
    gastos = models.ManyToManyField('Gasto', blank=True)
    anotacoes = models.ManyToManyField('Anotacoe', blank=True)

    telefone = models.CharField(max_length=11, null=False, blank=True, help_text='Digite apenas números')
    locat_slots = models.IntegerField(default=5)
    data_eventos_i = models.DateField(blank=True, null=True)
    itens_eventos = models.CharField(blank=True, null=True, max_length=31, default=[1, 2, 3, 4, 5, 6])
    qtd_eventos = models.IntegerField(blank=True, null=True, default=10)
    ordem_eventos = models.IntegerField(default=1, blank=False)

    def get_absolute_url(self):
        return reverse('navbar:DashBoard', args=[str(self.pk, )])


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
    com_imoveis = models.ManyToManyField('Imovei', blank=True, related_name='imoveis')
    com_contratos = models.ManyToManyField('Contrato', blank=True, related_name='contratos')

    nome = models.CharField(max_length=100, blank=False, verbose_name='Nome Completo')
    docs = models.ImageField(upload_to='documentos/%Y/%m/', blank=True, verbose_name='Documentos')
    RG = models.CharField(max_length=11, null=False, blank=False, help_text='Digite apenas números')
    CPF = models.CharField(max_length=11, null=False, blank=False, help_text='Digite apenas números')
    ocupacao = models.CharField(max_length=85, verbose_name='Ocupação')
    telefone1 = models.CharField(max_length=11, verbose_name='Telefone 1', help_text='Digite apenas números')
    telefone2 = models.CharField(max_length=11, blank=True, verbose_name='Telefone 2',
                                 help_text='Digite apenas números')
    email = models.EmailField(max_length=45, blank=True)
    nacionalidade = models.CharField(max_length=40, blank=False, default='Brasileiro(a)')
    estadocivil = models.IntegerField(blank=False, verbose_name='Estado Civil', choices=estados_civis)
    data_registro = models.DateTimeField(auto_now_add=True)
    objects = LocatariosManager()

    def get_absolute_url(self):
        return reverse('navbar:Locatários', args=[str(self.pk, )])

    def __str__(self):
        return f'{self.nome}'

    def imoveis_alugados(self):
        x = Imovei.objects.filter(com_locatario=self.pk)
        return x


class ImovGrupo(models.Model):
    do_usuario = models.ForeignKey('Usuario', null=True, blank=True,
                                   on_delete=models.CASCADE)

    nome = models.CharField(max_length=35, blank=False, verbose_name='Criar Grupo')
    imoveis = models.ManyToManyField('Imovei', blank=True)

    def get_absolute_url(self):
        return reverse('navbar:Criar Grupo Imóveis', args=[str(self.pk, )])

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ('nome',)


class ImoveiManager(models.Manager):
    def disponiveis(self):
        return self.filter(com_locatario=None)

    def ocupados(self):
        return self.exclude(com_locatario__isnull=True)


class Imovei(models.Model):
    do_locador = models.ForeignKey('Usuario', blank=False, on_delete=models.CASCADE)
    com_locatario = models.ForeignKey('Locatario', blank=True, null=True, on_delete=models.SET_NULL)
    contrato_atual = models.ForeignKey('Contrato', blank=True, null=True, on_delete=models.SET_NULL)
    # /\ one to one corrige
    grupo = models.ForeignKey('ImovGrupo', blank=True, null=True, on_delete=models.SET_NULL)

    nome = models.CharField(max_length=25, blank=False, verbose_name='Rótulo')
    endereco = models.CharField(max_length=150, blank=False, verbose_name='Endereço')
    uc_energia = models.CharField(max_length=15, blank=True, verbose_name='Matrícula de Energia')
    uc_agua = models.CharField(max_length=15, blank=True, verbose_name='Matrícula de Saneamento')
    data_registro = models.DateTimeField(default=datetime.now)
    objects = ImoveiManager()

    def get_absolute_url(self):
        return reverse('navbar:Imóveis', args=[str(self.pk), ])

    def __str__(self):
        return f'{self.nome} ({self.grupo})'

    def nogrupo(self):
        return '' if self.grupo is None else self.grupo

    def esta_ocupado(self):
        return False if self.com_locatario is None else True


class Contrato(models.Model):
    do_locador = models.ForeignKey('Usuario', null=True, blank=True, on_delete=models.CASCADE)
    do_locatario = models.ForeignKey('Locatario', on_delete=models.CASCADE,
                                     verbose_name='Locatário')
    do_imovel = models.ForeignKey(Imovei, on_delete=models.CASCADE, verbose_name='do imóvel')

    data_entrada = models.DateField(blank=False, verbose_name='Data de Entrada')
    data_saida = models.DateField(blank=False, verbose_name='Data de Saída')
    valor_mensal = models.CharField(max_length=9, verbose_name='Valor Mensal (R$): ', blank=False,
                                    help_text='Digite apenas números')
    dia_vencimento = models.IntegerField(blank=False, validators=[MaxValueValidator(28), MinValueValidator(1)],
                                         verbose_name='Dia do vencimento', help_text='(1-28)')
    em_posse = models.BooleanField(default=False, null=False, help_text='Marque quando receber a sua via assinada e '
                                                                       'registrada em cartório')
    rescindido = models.BooleanField(default=False, null=False, help_text='Marque caso haja rescisão do contrato')
    vencido = models.BooleanField(default=False, null=False)
    data_de_rescisao = models.DateField(blank=True, verbose_name='Data da rescisão', null=True)
    data_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            CheckConstraint(check=Q(data_saida__gt=F('data_entrada')), name='entrada_saida'),
        ]

    def get_absolute_url(self):
        return reverse('navbar:Contratos', args=[str(self.pk), ])

    def __str__(self):
        return f'({self.do_locatario.nome.split()[:2][0]} {self.do_locatario.nome.split()[:2][1]} ' \
               f'- {self.do_imovel.nome} - {self.data_entrada.strftime("%d/%m/%Y")})'

    def valor_br(self):
        return valor_br(self.valor_mensal)

    def valor_do_contrato(self):
        pass

    def total_quitado(self):
        pass

    def total_pg(self):
        pass

    def em_maos(self):
        return 'Sim' if self.em_posse else 'Não'


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

    valor_pago = models.CharField(max_length=9, verbose_name='Valor Pago (R$): ', blank=False)
    data_pagamento = models.DateTimeField(blank=False, verbose_name='Data do Pagamento')
    recibo = models.BooleanField(default=True, verbose_name='Recibo Entregue',
                                 help_text='Marque quando o recido estiver esntregue')
    data_de_recibo = models.DateTimeField(blank=True, verbose_name='Data em que foi marcado recibo entregue', null=True)
    forma = models.IntegerField(blank=False, choices=lista_pagamentos, verbose_name='Forma de Pagamento')
    data_criacao = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('navbar:Pagamentos', args=[(str(self.pk)), ])

    def valor_br(self):
        return valor_br(self.valor_pago)

    def __str__(self):
        return f'{self.do_locatario} - R${self.valor_br()} - {self.data_pagamento.strftime("%D")}'


class Gasto(models.Model):
    do_locador = models.ForeignKey('Usuario', null=False, on_delete=models.CASCADE)
    do_imovel = models.ForeignKey('Imovei', blank=False, on_delete=models.CASCADE)

    valor = models.CharField(max_length=9, verbose_name='Valor Gasto (R$): ', blank=False)
    data = models.DateTimeField(blank=False)
    observacoes = models.TextField(max_length=500, blank=True, verbose_name='Observações')
    comprovante = models.ImageField(upload_to='comprovante', blank=True, verbose_name='Comporvante')
    data_criacao = models.DateTimeField(auto_now_add=True)

    def get_alsolute_url(self):
        return reverse('navbar:Gastos', args=[(str(self.pk)), ])

    def valor_br(self):
        return valor_br(self.valor)

    def __str__(self):
        return f'{self.observacoes[:20]} - {self.valor_br()} - {self.data.strftime("%D")}'


class Anotacoe(models.Model):
    do_usuario = models.ForeignKey('Usuario', null=False, on_delete=models.CASCADE)

    titulo = models.CharField(blank=False, max_length=100, verbose_name='Título')
    data_registro = models.DateTimeField(blank=True)
    texto = models.TextField(blank=False)

    def get_absolute_url(self):
        return reverse('navbar:Anotações', args=[(str(self.pk)), ])

    def __str__(self):
        return f'{self.titulo} - {self.data_registro.strftime("%D")}'


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
    imagem = models.ImageField(upload_to='mensagens/', blank=True)

    def get_absolute_url(self):
        return reverse('home:Mensagem pro Desenvolvedor', args=[(str(self.pk)), ])

    def __str__(self):
        return f'{self.do_usuario} - {self.titulo} - {self.data}'
