import string, secrets
from datetime import datetime, timedelta
from math import floor

from dateutil.relativedelta import relativedelta
from num2words import num2words

from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator, MinValueValidator, \
    MaxValueValidator, FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.template.defaultfilters import date as data_ptbr
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
        secrets.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(10))
    return f'{con_codigo[:10]}'


def parcela_uuid():
    recibo_codigo = ''.join(
        secrets.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in
        range(6))
    return f'{recibo_codigo[:3]}-{recibo_codigo[3:]}'


# Gerar o código para o contrato:
def gerar_codigo_contrato():
    codigos_existentes = list(Contrato.objects.all().values("codigo").values_list('codigo', flat=True))
    while True:
        con_codigo = ''.join(
            secrets.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(10))
        if con_codigo not in codigos_existentes:
            return f'{con_codigo[:5]}-{con_codigo[5:]}'


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
    tickets = models.IntegerField(default=50)
    # Outros poderão ter acesso ao uuid por cópias digitais de pdfs que poderão ser repassadas pelo usuário

    locat_slots = models.IntegerField(default=2)

    vis_ger_ultim_order_by = models.CharField(default='vencimento_atual', null=True, blank=True, max_length=60)

    data_eventos_i = models.DateField(blank=True, null=True)
    itens_eventos = models.CharField(blank=True, null=True, max_length=31, default=['1', '2', '3', '4', '5', '6'])
    qtd_eventos = models.IntegerField(blank=True, null=True, default=25)
    ordem_eventos = models.IntegerField(default=1, blank=False)

    recibo_ultimo = models.ForeignKey('Contrato', null=True, blank=True, related_name='usuario_recibo_set',
                                      on_delete=models.SET_NULL)
    recibo_preenchimento = models.IntegerField(null=True, blank=True)

    tabela_ultima_data_ger = models.IntegerField(null=True, blank=True)
    tabela_meses_qtd = models.IntegerField(null=True, blank=True)
    tabela_imov_qtd = models.IntegerField(null=True, blank=True)

    contrato_ultimo = models.ForeignKey('Contrato', null=True, blank=True, related_name='usuario_contrato_set',
                                        on_delete=models.SET_NULL)

    def locat_auto_registro_link(self):
        return reverse('home:Locatario Auto-Registro', args=[self.username, self.uuid])

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

    def arrecadacao_total(self):
        try:
            total = 0
            pagamentos = Pagamento.objects.filter(ao_locador=self).values_list('valor_pago')

            for pagamento in pagamentos:
                total += int(pagamento[0])

            return valor_format(str(total))
        except:
            return None

    def arrecadacao_mensal(self):
        try:
            contratos_user = Contrato.objects.ativos().filter(do_locador=self)
            arrecadacao_mensal = 0
            for contrato in contratos_user:
                arrecadacao_mensal += int(contrato.valor_mensal)
            return valor_format(str(arrecadacao_mensal))
        except:
            return None

    def valor_total_contratos_ativos(self):
        try:
            contratos_user = Contrato.objects.ativos().filter(do_locador=self)
            valor_total_contratos_ativos = 0
            for contrato in contratos_user:
                valor_total_contratos_ativos += int(contrato.valor_do_contrato())
            return valor_format(str(valor_total_contratos_ativos))
        except:
            return None

    def valor_total_contratos(self):
        try:
            contratos_user = Contrato.objects.filter(do_locador=self)
            valor_total_contratos = 0
            for contrato in contratos_user:
                valor_total_contratos += int(contrato.valor_do_contrato())
            return valor_format(str(valor_total_contratos))
        except:
            return None

    def tem_slot_disponivel(self):
        slots = Slot.objects.filter(do_usuario=self)
        for slot in slots:
            if slot.imovel() is None:
                return True
        return False


class SlotsManager(models.Manager):
    def ativos(self):
        slots_qs = self.all()
        lista = []
        for slot in slots_qs:
            if slot.ativado() is True:
                lista.append(slot.pk)
        slots_ativos = Slot.objects.filter(pk__in=lista)
        return slots_ativos

    def inativos(self):
        slots_qs = self.all()
        lista = []
        for slot in slots_qs:
            if slot.ativado() is False:
                lista.append(slot.pk)
        slots_inativos = Slot.objects.filter(pk__in=lista)
        return slots_inativos

    def inativos_com_imovel(self):
        slots_qs = self.all()
        lista = []
        for slot in slots_qs:
            if slot.ativado() is False and slot.imovel() is not None:
                lista.append(slot.pk)
        slots_inativos = Slot.objects.filter(pk__in=lista)
        return slots_inativos


class Slot(models.Model):
    do_usuario = models.ForeignKey('Usuario', null=False, blank=False, on_delete=models.CASCADE)
    da_tarefa = models.OneToOneField('Tarefa', null=True, blank=True, on_delete=models.SET_NULL)

    gratuito = models.BooleanField(null=False, default=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    tickets = models.PositiveIntegerField(default=0)
    objects = SlotsManager()

    class Meta:
        verbose_name_plural = 'Slots'
        ordering = ('pk',)

    def __str__(self):
        return (f'{self.pk}: {"Gratuito" if self.gratuito else "Pago"}/Criado: {self.criado_em}'
                f'/Tickets: {self.tickets}/{self.do_usuario}/{self.imovel()}')

    def imovel(self):
        try:
            slots = Slot.objects.filter(do_usuario=self.do_usuario).order_by('pk')
            imoveis = Imovei.objects.filter(do_locador=self.do_usuario).order_by('data_registro')
            return imoveis[list(slots).index(self)]
        except:
            return None

    def vencimento(self):
        # colocar para vencer um dia após, não zero(evitar reclamações dos usuários/não pode comer tempo deles)
        data = self.criado_em + relativedelta(days=int(self.tickets)*30)
        return data.date()

    def dias_ativo(self):
        inicial = self.criado_em.date()
        final = self.vencimento()
        delta = final - inicial
        return int(delta.days)

    def dias_passados(self):
        inicial = self.criado_em.date()
        final = datetime.today().date()
        delta = final - inicial
        return int(delta.days)

    def dias_restando(self):
        dias_ativo = self.dias_ativo()
        dias_pasados = self.dias_passados()
        dias_restando = dias_ativo - dias_pasados
        return dias_restando if dias_restando >= 0 else 0

    def tickets_restando(self):
        """Aqui deve retornar os tickets(self.tickets) menos a quantia de tickets equivalentes aos dias que já passaram
        esde a criação do slot até hoje"""
        tickets_passados = floor(self.dias_passados()/30)
        tickets_restando = self.tickets - tickets_passados
        return tickets_restando if tickets_restando >= 0 else 0

    def ativado(self):
        if self.gratuito:
            return True
        else:
            return False if datetime.today().date() >= self.vencimento() else True

    def borda(self):
        if self.gratuito:
            return 'border-success'
        else:
            return 'border-secondary' if self.ativado() else 'border-warning'


class LocatariosManager(models.Manager):
    def nao_temporarios(self):
        # Locatarios cadastrados pelos usuários, não que se cadastraram pelo link(Portanto seus cadastros
        # estão no modo temporário(para aprovação))
        return self.exclude(temporario=True)


class Locatario(models.Model):
    do_locador = models.ForeignKey('Usuario', null=True, blank=True, on_delete=models.CASCADE)
    da_tarefa = models.OneToOneField('Tarefa', null=True, blank=True, on_delete=models.SET_NULL)

    nome = models.CharField(max_length=100, blank=False, verbose_name='Nome Completo')
    docs = ResizedImageField(size=[1280, None], upload_to='locatarios_docs/%Y/%m/', null=True, blank=True,
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
    telefone2 = models.CharField(max_length=11, null=True, blank=True, verbose_name='Telefone 2',
                                 help_text='Celular/Digite apenas números',
                                 validators=[MinLengthValidator(11), MaxLengthValidator(11), apenas_numeros])
    email = models.EmailField(max_length=45, null=True, blank=True)
    nacionalidade = models.CharField(max_length=40, blank=False, default='Brasileiro(a)')
    estadocivil = models.IntegerField(blank=False, verbose_name='Estado Civil', choices=estados_civis)
    data_registro = models.DateTimeField(auto_now_add=True)
    temporario = models.BooleanField(null=True)
    objects = LocatariosManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["CPF", "do_locador"], name="cpf_locatario_por_usuario"),
        ]
        verbose_name_plural = 'Locatários'

    def __str__(self):
        return f'{self.nome}'

    def com_contratos(self):
        contratos = Contrato.objects.ativos().filter(do_locador=self.do_locador, do_locatario=self)
        return contratos or None

    def com_imoveis(self):
        contratos = self.com_contratos()
        contratos_ativos = []
        for contrato in contratos:
            contratos_ativos.append(contrato)
        if contratos_ativos:
            imoveis_pk = [contrato.do_imovel.pk for contrato in contratos_ativos]
            imoveis = Imovei.objects.filter(pk__in=imoveis_pk)
            return imoveis
        else:
            return None

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
        else:
            return None

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

    class Meta:
        verbose_name_plural = 'Grupos de imóveis'
        ordering = ('nome',)

    def __str__(self):
        return self.nome

    def arrecadacao_total(self):
        try:
            total = 0
            imoveis = Imovei.objects.filter(grupo=self)
            for imovel in imoveis:
                total += imovel.receita_acumulada()
            return valor_format(str(total))
        except:
            return None

    def arrecadacao_mensal(self):
        try:
            imoveis = Imovei.objects.filter(grupo=self)
            contratos_user = Contrato.objects.ativos().filter(do_imovel__in=imoveis, do_locador=self.do_usuario)
            arrecadacao_mensal = 0
            for contrato in contratos_user:
                arrecadacao_mensal += int(contrato.valor_mensal)
            return valor_format(str(arrecadacao_mensal))
        except:
            return None

    def valor_total_contratos_ativos(self):
        try:
            imoveis = Imovei.objects.filter(grupo=self)
            contratos_user = Contrato.objects.ativos().filter(do_imovel__in=imoveis, do_locador=self.do_usuario)
            valor_total_contratos_ativos = 0
            for contrato in contratos_user:
                valor_total_contratos_ativos += int(contrato.valor_do_contrato())
            return valor_format(str(valor_total_contratos_ativos))
        except:
            return None

    def valor_total_contratos(self):
        try:
            imoveis = Imovei.objects.filter(grupo=self)
            contratos_user = Contrato.objects.filter(do_imovel__in=imoveis, do_locador=self.do_usuario)
            valor_total_contratos = 0
            for contrato in contratos_user:
                valor_total_contratos += int(contrato.valor_do_contrato())
            return valor_format(str(valor_total_contratos))
        except:
            return None


class ImoveiManager(models.Manager):
    def ativos(self):
        imoveis_qs = self
        lista = []
        for imovel in imoveis_qs:
            if imovel.esta_ocupado() is True:
                lista.append(imovel.pk)
        imoveis_ativos = Imovei.objects.filter(pk__in=lista)
        return imoveis_ativos


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
    grupo = models.ForeignKey('ImovGrupo', blank=True, null=True, on_delete=models.SET_NULL)

    nome = models.CharField(max_length=25, blank=False, verbose_name='Rótulo')
    cep = models.CharField(max_length=8, blank=False, verbose_name='CEP',
                           validators=[MinLengthValidator(8), MaxLengthValidator(8), apenas_numeros])
    endereco = models.CharField(max_length=150, blank=False, verbose_name='Endereço')
    numero = models.IntegerField(blank=False,
                                 validators=[MinValueValidator(1), MaxValueValidator(999999), apenas_numeros])
    complemento = models.CharField(max_length=80, null=True, blank=True)
    bairro = models.CharField(max_length=30, blank=False)
    cidade = models.CharField(max_length=30, blank=False)
    estado = models.CharField(max_length=2, blank=False, choices=estados)
    uc_energia = models.CharField(max_length=15, null=True, blank=True, verbose_name='Matrícula de Energia',
                                  validators=[MinLengthValidator(4), MaxLengthValidator(15)])
    uc_agua = models.CharField(max_length=15, null=True, blank=True, verbose_name='Matrícula de Saneamento',
                               validators=[MinLengthValidator(4), MaxLengthValidator(15)])
    data_registro = models.DateTimeField(default=datetime.now)
    objects = ImoveiManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["nome", "do_locador"], name="nome_imovel_por_usuario"),
        ]
        verbose_name_plural = 'Imóveis'
        ordering = ['-nome']

    def __str__(self):
        return f'{self.nome} ({self.grupo if self.grupo else "Sem grupo"})'

    def contrato_atual(self):
        contratos = Contrato.objects.ativos().filter(do_locador=self.do_locador, do_imovel=self)
        if contratos:
            return contratos[0]
        else:
            return None

    def contrato_todos(self):
        contratos = Contrato.objects.filter(do_locador=self.do_locador, do_imovel=self)
        if contratos:
            return contratos
        else:
            return None

    def com_locatario(self):
        if self.contrato_atual():
            return self.contrato_atual().do_locatario
        else:
            return None

    def nogrupo(self):
        return '' if self.grupo is None else self.grupo

    def esta_ocupado(self):
        return False if self.com_locatario is None else True

    def f_cep(self):
        return cep_format(self.cep)

    def endereco_base(self):
        complemento = f'({self.complemento})'
        return f'{self.endereco}, Nº{self.numero}{complemento if self.complemento else ""} - {self.bairro}'

    def endereco_completo(self):
        return f'{self.endereco_base()} - {self.cidade}/{self.estado}, {self.f_cep()}'

    def receita_acumulada(self):
        parcelas = Parcela.objects.filter(do_imovel=self, apagada=False)
        total = 0
        for parcela in parcelas:
            total += int(parcela.tt_pago)
        return total

    def receita_acumulada_format(self):
        return valor_format(str(self.receita_acumulada()))

    def em_slot(self):
        """ retorna true se estiver em slot e false se não """
        slots = Slot.objects.filter(do_usuario=self.do_locador)
        imoveis_em_slot = []
        for slot in slots:
            if slot.ativado():
                imoveis_em_slot.append(slot.imovel())
        return True if self in imoveis_em_slot else False


class ContratoManager(models.Manager):
    def ativos(self):
        hoje = datetime.today().date()
        contratos_qs = self.filter(em_posse=True, rescindido=False, data_entrada__lte=hoje)
        lista = []
        for contrato in contratos_qs:
            if contrato.periodo_ativo_hoje() is True:
                lista.append(contrato.pk)
        contratos_ativos = Contrato.objects.filter(pk__in=lista)
        return contratos_ativos

    def ativos_margem(self):
        hoje = datetime.today().date()
        contratos_qs = self.filter(rescindido=False, data_entrada__lte=hoje)
        lista = []
        for contrato in contratos_qs:
            if contrato.periodo_ativo_hoje() or contrato.periodo_ativo_futuramente() or \
                    contrato.periodo_ativo_xx_dias_atras():
                lista.append(contrato.pk)
        contratos_ativos = Contrato.objects.filter(pk__in=lista)
        return contratos_ativos

    def inativos(self):
        pass

    def ativos_e_no_slot(self):
        hoje = datetime.today().date()
        contratos_qs = self.filter(em_posse=True, rescindido=False, data_entrada__lte=hoje)
        lista = []
        for contrato in contratos_qs:
            if contrato.periodo_ativo_hoje() is True and contrato.do_imovel.em_slot() is True:
                lista.append(contrato.pk)
        contratos_ativos_slot = Contrato.objects.filter(pk__in=lista)
        return contratos_ativos_slot

    def ativos_e_sem_slot(self):
        hoje = datetime.today().date()
        contratos_qs = self.filter(em_posse=True, rescindido=False, data_entrada__lte=hoje)
        lista = []
        for contrato in contratos_qs:
            if contrato.periodo_ativo_hoje() is True and contrato.do_imovel.em_slot() is False:
                lista.append(contrato.pk)
        contratos_ativos_sem_slot = Contrato.objects.filter(pk__in=lista)
        return contratos_ativos_sem_slot


class Contrato(models.Model):
    do_locador = models.ForeignKey('Usuario', null=True, blank=True, on_delete=models.CASCADE)
    do_locatario = models.ForeignKey('Locatario', on_delete=models.CASCADE,
                                     verbose_name='Locatário')
    do_imovel = models.ForeignKey('Imovei', on_delete=models.CASCADE, verbose_name='No imóvel')
    da_tarefa = models.OneToOneField('Tarefa', null=True, blank=True, on_delete=models.SET_NULL)

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
    codigo = models.CharField(null=False, editable=False, max_length=11, default=gerar_codigo_contrato)
    data_de_rescisao = models.DateField(blank=True, verbose_name='Data da rescisão', null=True)
    recibos_pdf = models.FileField(upload_to='recibos_docs/%Y/%m/', blank=True, verbose_name='Recibos')
    data_registro = models.DateTimeField(auto_now_add=True)
    objects = ContratoManager()

    class Meta:
        ordering = ['-data_entrada']

    def __str__(self):
        return f'({self.do_locatario.primeiro_ultimo_nome()}-{self.do_imovel.nome}-' \
               f'{self.data_entrada.strftime("%m/%Y")})'

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
        valores = Pagamento.objects.filter(ao_contrato=self).values_list('valor_pago')
        valor_tt = 0
        for valor in valores:
            valor_tt += int(valor[0])
        return valor_tt

    def total_pg_format(self):
        if self.total_quitado() is None:
            return 'R$0,00'
        else:
            return valor_format(str(self.total_quitado()))

    def falta_pg(self):
        if self.total_quitado() is None:
            return self.valor_do_contrato()
        else:
            return str((int(self.valor_mensal) * int(self.duracao)) - self.total_quitado())

    def falta_pg_format(self):
        return valor_format(self.falta_pg())

    def em_maos(self):
        return 'Sim' if self.em_posse else 'Não'

    def data_saida(self):
        data = self.data_entrada + relativedelta(months=self.duracao)
        return data

    def periodo_vencido(self):
        return True if self.data_saida() > datetime.today() else False

    def periodo_ativo_hoje(self):
        hoje = datetime.today().date()
        return True if self.data_entrada <= hoje <= self.data_saida() else False

    def periodo_ativo_futuramente(self):
        return True if self.data_entrada > datetime.today().date() else False

    def periodo_ativo_xx_dias_atras(self, dias=45):
        return True if self.data_saida() >= datetime.today().date() + timedelta(days=-dias) else False

    def pagamento_total(self):
        pagamentos = Pagamento.objects.filter(ao_contrato=self.pk).values('valor_pago')
        valor_tt = 0
        for valor in pagamentos:
            valor_tt += int(valor['valor_pago'])
        return valor_tt

    def duracao_dias(self):
        delta = self.data_saida() - self.data_entrada
        return delta.days

    def transcorrido_dias(self):
        delta = datetime.today().date() - self.data_entrada
        return delta.days

    def faltando_dias(self):
        return self.duracao_dias() - self.transcorrido_dias()

    def passou_do_limite(self):
        return True if int(self.faltando_dias()) <= 30 else False

    def recibos_entregues_qtd(self):
        x = Parcela.objects.filter(do_contrato=self, recibo_entregue=True).count()
        return x

    def parcelas_pagas_qtd(self):
        numero = self.pagamento_total() / int(self.valor_mensal)
        return int(floor(numero))

    def quitado(self):
        return True if self.total_quitado() == int(self.valor_do_contrato()) else False

    def title_pagou_parcelas(self):
        if self.parcelas_pagas_qtd() > 0:
            plural = 's' if self.parcelas_pagas_qtd() > 1 else ''
            return f'Quitou {self.parcelas_pagas_qtd()} parcela{plural} de {self.duracao}'
        else:
            return 'Nenhuma parcela quitada ainda'

    def faltando_recibos_qtd(self):
        try:
            return self.parcelas_pagas_qtd() - self.recibos_entregues_qtd()
        except:
            return None

    def duracao_meses_por_extenso(self):
        return num2words(self.duracao, lang='pt_BR')

    def dia_vencimento_por_extenso(self):
        return num2words(self.dia_vencimento, lang='pt_BR')

    def vencimento_atual(self):
        parcela_n_kit = Parcela.objects.filter(do_contrato=self, apagada=False).order_by('data_pagm_ref')
        parcelas = []
        for parcela in parcela_n_kit:
            if int(parcela.tt_pago) < int(self.valor_mensal) or int(parcela.tt_pago) == 0:
                parcelas.append(parcela)
        return parcelas[0].data_pagm_ref if parcelas else None

    def vencimento_atual_textual(self):
        txt = '📃✔️'
        title = 'O contrato está quitado'
        if self.vencimento_atual() is not None:
            hoje = datetime.today().date()
            vencim_atual = self.vencimento_atual()
            delta = hoje - vencim_atual
            delta2 = vencim_atual - hoje
            if vencim_atual == hoje + relativedelta(days=-1):
                txt = f'⭕ Venceu ontem ({vencim_atual.strftime("%d/%m/%Y")})'
                title = ''
            elif vencim_atual < hoje + relativedelta(days=-1):
                txt = f'⭕ Venceu em {vencim_atual.strftime("%d/%m/%Y")} ({delta.days} dias atrás)'
                title = ''
            elif vencim_atual == hoje:
                txt = f'🟡 Vence hoje ({vencim_atual.strftime("%d/%m/%Y")})'
                title = ''
            elif vencim_atual == hoje + relativedelta(days=+1):
                txt = f'🟡 Vencerá amanhã ({vencim_atual.strftime("%d/%m/%Y")})'
                title = ''
            elif vencim_atual > hoje + relativedelta(days=+1):
                if delta2.days <= 5:
                    txt = f'🟡 Vencerá em {vencim_atual.strftime("%d/%m/%Y")} (em {delta2.days} dias)'
                else:
                    txt = f'Vencerá em {vencim_atual.strftime("%d/%m/%Y")} (em {delta2.days} dias)'
                title = ''
        return txt, title

    def divida_atual_meses(self):
        parcelas = Parcela.objects.filter(do_contrato=self, apagada=False, data_pagm_ref__lte=datetime.today().date())
        parcelas_vencidas_n_quitadas = 0
        for parcela in parcelas:
            if int(parcela.tt_pago) < int(self.valor_mensal):
                parcelas_vencidas_n_quitadas += 1
        return parcelas_vencidas_n_quitadas

    def divida_atual_valor(self):
        parcelas = Parcela.objects.filter(do_contrato=self, apagada=False, data_pagm_ref__lte=datetime.today().date())
        parcelas_vencidas_n_quitadas = []
        for parcela in parcelas:
            if int(parcela.tt_pago) < int(self.valor_mensal) and parcela.apagada is False:
                parcelas_vencidas_n_quitadas.append(int(parcela.tt_pago))
        soma_tt_pg = sum([i for i in parcelas_vencidas_n_quitadas])
        valor = (len(parcelas_vencidas_n_quitadas) * int(self.valor_mensal)) - (int(soma_tt_pg) if soma_tt_pg else 0)
        return valor, valor_format(str(valor))


class ContratoModelo(models.Model):
    titulo = models.CharField(blank=False, max_length=120, verbose_name='', help_text='Titulo')
    autor = models.ForeignKey('Usuario', blank=False, null=True, related_name='contratomod_autor_set',
                              on_delete=models.SET_NULL)
    descricao = models.CharField(blank=True, max_length=480, verbose_name='', help_text='Descrição')
    corpo = RichTextField(null=True, blank=True, verbose_name='')
    data_criacao = models.DateTimeField(auto_now_add=True)
    variaveis = models.JSONField(null=True, blank=True)
    condicoes = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Modelos de contratos'

    def __str__(self):
        return f'{self.titulo}'

    def display_variaveis(self):
        variaveis = []
        for variavel in list(self.variaveis):
            if variavel in modelo_variaveis:
                variaveis.append([modelo_variaveis[variavel][0], modelo_variaveis[variavel][1]])
        return variaveis if len(variaveis) > 0 else False

    def display_condicoes(self):
        condicoes = []
        for condicao in list(self.condicoes):
            if condicao in modelo_condicoes:
                condicoes.append([modelo_condicoes[condicao][0], modelo_condicoes[condicao][1]])
        return condicoes if len(condicoes) > 0 else False


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

    class Meta:
        verbose_name_plural = 'Configs de contratos'

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
    data_pagm_ref = models.DateField(null=False, blank=False,
                                     help_text='Data referente ao vencimento do pagamento desta parcela')
    tt_pago = models.CharField(max_length=9, blank=False, default=0)
    recibo_entregue = models.BooleanField(default=False)
    apagada = models.BooleanField(default=False)

    def __str__(self):
        return (f'Parcela do contr.: {str(self.do_contrato.codigo)}/{self.do_locatario.primeiro_ultimo_nome()}/'
                f'{self.do_imovel}({self.data_pagm_ref.strftime("%B/%Y")})')

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
            parcelas = list(
                Parcela.objects.filter(do_contrato=self.do_contrato, apagada=False).values_list('pk', flat=True))
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

    def de_contrato_ativo(self):
        if (self.do_contrato.periodo_ativo_hoje() and self.do_contrato.em_posse is True and self.do_contrato.rescindido
                is False):
            return True
        else:
            return False


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

    def valor_format(self):
        return valor_format(self.valor_pago)

    def __str__(self):
        return f'{self.do_locatario} - R${self.valor_format()} - {self.data_pagamento.strftime("%D")}'


class Gasto(models.Model):
    do_locador = models.ForeignKey('Usuario', null=False, on_delete=models.CASCADE)
    do_imovel = models.ForeignKey('Imovei', blank=True, null=True, on_delete=models.CASCADE,
                                  help_text='Deixe em branco para registrar um gasto avulso')

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

    class Meta:
        verbose_name_plural = 'Anotações'

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


class TarefaManager(models.Manager):
    def tarefas_novas(self):
        tarefas_qs = self.filter(apagada=False)
        lista = []
        for tarefa in tarefas_qs:
            if tarefa.tarefa_nova() is True:
                lista.append(tarefa.pk)
        tarefas_novas = Tarefa.objects.filter(pk__in=lista)
        return tarefas_novas

    def tarefas_historico(self):
        tarefas_qs = self.filter(apagada=False)
        lista = []
        for tarefa in tarefas_qs:
            if tarefa.tarefa_nova() is False:
                lista.append(tarefa.pk)
        tarefas_novas = Tarefa.objects.filter(pk__in=lista)
        return tarefas_novas


class Tarefa(models.Model):
    do_usuario = models.ForeignKey('Usuario', null=False, on_delete=models.CASCADE)
    autor_classe = models.ForeignKey(ContentType, null=False, on_delete=models.CASCADE)
    objeto_id = models.PositiveIntegerField(null=False)
    content_object = GenericForeignKey('autor_classe', 'objeto_id')

    data_registro = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(null=True)
    apagada = models.BooleanField(default=False)
    data_lida = models.DateTimeField(null=True)
    objects = TarefaManager()

    class Meta:
        ordering = ['-data_registro']

    def __str__(self):
        return f'Tarefa: classe:{self.autor_classe}/objeto_id:{self.objeto_id}'

    def autor_tipo(self):
        if self.autor_classe == ContentType.objects.get_for_model(Parcela):
            return 1
        elif self.autor_classe == ContentType.objects.get_for_model(Anotacoe):
            return 2
        elif self.autor_classe == ContentType.objects.get_for_model(Contrato):
            return 3
        elif self.autor_classe == ContentType.objects.get_for_model(Sugestao):
            return 4
        elif self.autor_classe == ContentType.objects.get_for_model(Locatario):
            return 5
        elif self.autor_classe == ContentType.objects.get_for_model(Slot):
            return 6

    def autor_tipo_display(self):
        if self.autor_classe == ContentType.objects.get_for_model(Parcela):
            return '🧾 Recibo'
        elif self.autor_classe == ContentType.objects.get_for_model(Anotacoe):
            return '🗒️ Tarefa'
        elif self.autor_classe == ContentType.objects.get_for_model(Contrato):
            return '📃 Contrato'
        elif self.autor_classe == ContentType.objects.get_for_model(Sugestao):
            return '⚠️ Aviso'
        elif self.autor_classe == ContentType.objects.get_for_model(Locatario):
            return '👨‍💼 Locatário'
        elif self.autor_classe == ContentType.objects.get_for_model(Slot):
            return '⚠️ Aviso'

    def tarefa_nova(self):
        # Vai retornar True ou none, True se o autor desta tarefa estiver marcado como concluido(ps: concluídos em
        # seus respectivos formatos; ex: recibo: 'recibo_entregue', ex: Anotação: 'feito', ex: contrato: 'em_posse',
        # ex: sugestão: 'neste caso utiliza o próprio parâmetro 'lida' desta model.'...)
        # Retorna none caso o objeto não exista, (caso gere um except)
        if self.autor_classe == ContentType.objects.get_for_model(Parcela):
            try:
                return True if self.content_object.recibo_entregue is False else False
            except:
                return None
        elif self.autor_classe == ContentType.objects.get_for_model(Anotacoe):
            try:
                return True if self.content_object.feito is False else False
            except:
                return None
        elif self.autor_classe == ContentType.objects.get_for_model(Contrato):
            try:
                return True if self.content_object.em_posse is False else False
            except:
                return None
        elif self.autor_classe == ContentType.objects.get_for_model(Sugestao):
            try:
                return False if self.lida else True
            except:
                return None
        elif self.autor_classe == ContentType.objects.get_for_model(Locatario):
            try:
                return True if self.content_object.temporario is True else False
            except:
                return None
        elif self.autor_classe == ContentType.objects.get_for_model(Slot):
            try:
                return False if self.lida else True
            except:
                return None

    def borda(self):
        if self.autor_classe == ContentType.objects.get_for_model(Parcela):
            return 'border-white'
        elif self.autor_classe == ContentType.objects.get_for_model(Anotacoe):
            return 'border-warning'
        elif self.autor_classe == ContentType.objects.get_for_model(Contrato):
            return 'border-primary'
        elif self.autor_classe == ContentType.objects.get_for_model(Sugestao):
            return 'border-success'
        elif self.autor_classe == ContentType.objects.get_for_model(Locatario):
            return 'border-secondary'
        elif self.autor_classe == ContentType.objects.get_for_model(Slot):
            return 'border-success'

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
                tamanho_max_txt = 200
                nota = self.content_object
                cortado = f'{nota.texto[:tamanho_max_txt]}...'
                mensagem = f'''{nota.titulo}<br>{nota.texto if len(nota.texto) <= tamanho_max_txt else cortado}'''
            except:
                pass
        elif self.autor_classe == ContentType.objects.get_for_model(Contrato):
            try:
                contrato = self.content_object
                mensagem = f'''O contrato {contrato} foi criado com sucesso!<br><br>
                Depois de:<br>
                1. Gerar e imprimir o documento referente(Gerar PDF de Contrato), <br>
                2. Entregar ao locatário para reconhecimento em cartório, e <br>
                3. Recebê-lo novamente com a firma reconhecida. <br>
                Confirme a posse de sua via no botão abaixo para ativá-lo no sistema.'''
            except:
                pass
        elif self.autor_classe == ContentType.objects.get_for_model(Sugestao):
            try:
                tamanho_max_txt = 200
                sugestao = self.content_object
                cortado = f'{sugestao.corpo[:tamanho_max_txt]}...'
                mensagem = f'''Sua sugestão foi aprovada e está disponível para votação:<br>
                "{sugestao.corpo if len(sugestao.corpo) <= tamanho_max_txt else cortado}"'''
            except:
                pass
        elif self.autor_classe == ContentType.objects.get_for_model(Locatario):
            try:
                locatario = self.content_object
                mensagem = f'''Um novo locatário se registrou:<br>
                            Nome: {locatario.nome}<br>
                            Telefone: {cel_format(locatario.telefone1)}<br>
                            Email: {locatario.email}'''
            except:
                pass
        elif self.autor_classe == ContentType.objects.get_for_model(Slot):
            try:
                slot = self.content_object
                mensagem = f'''O imóvel {slot.imovel()} está desabilitado, por favor, acesse o painel para 
                habilitá-lo.'''
            except:
                pass
        return mensagem

    def definir_apagada(self):
        self.apagada = True
        self.save(update_fields=['apagada'])

    def restaurar(self):
        self.apagada = False
        self.save(update_fields=['apagada'])

    def definir_nao_lida(self):
        self.lida = False
        self.data_lida = None
        self.data_registro = datetime.now()
        self.save(update_fields=['lida', 'data_registro'])


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

    class Meta:
        verbose_name_plural = 'Mensagens ao Dev'

    def __str__(self):
        return f'{self.do_usuario} - {self.titulo} - {self.data_registro}'


class Sugestao(models.Model):
    do_usuario = models.ForeignKey('Usuario', null=True, blank=True, on_delete=models.CASCADE)
    da_tarefa = models.OneToOneField('Tarefa', null=True, blank=True, on_delete=models.SET_NULL)

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

    def __str__(self):
        return f'{self.do_usuario} - {self.corpo[:30]} - {self.data_registro}'

    def numero_de_likes(self):
        return self.likes.count()
