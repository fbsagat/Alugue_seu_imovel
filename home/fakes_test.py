from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from faker import Faker
from random import randrange, choice, sample

from home.models import ImovGrupo, Locatario, Imovei, Contrato, Usuario, estados

locales = 'pt_BR'
fake = Faker(locales)


def contratos_ficticios(request, locador):
    todos_locatarios = Locatario.objects.sem_imoveis().filter(do_locador=locador)
    do_locatario = choice(todos_locatarios)

    todos_imoveis = Imovei.objects.disponiveis().filter(do_locador=locador)
    do_imovel = choice(todos_imoveis)

    while True:
        dias = randrange(1, 100)
        entrada1 = fake.date_between(datetime.now().date() + timedelta(days=-dias * 2),
                                     datetime.now().date() + timedelta(days=-dias))
        dias2 = randrange(1, 30)
        entrada2 = fake.date_between(datetime.now().date() + timedelta(days=-dias2 - 5),
                                     datetime.now().date() + timedelta(days=-dias2))

        entrada = choice([entrada1, entrada2])

        duracao = randrange(4, 18)
        saida = entrada + relativedelta(months=duracao)

        contratos_deste_imovel = Contrato.objects.filter(do_imovel=do_imovel.pk)
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
        if permitido is True:
            data_entrada = entrada
            break

    zero_a_cem = randrange(0, 100)
    probabilidade_percentual = 75
    centavos = 0 if zero_a_cem <= probabilidade_percentual else randrange(10, 90, step=10)
    reais = [randrange(500, 1200, step=150), randrange(700, 3400, step=180), randrange(700, 3400, step=130),
             randrange(3400, 32000, step=1500)]
    valor_mensal = f'{choice(reais)}{centavos}'
    dia_vencimento = randrange(1, 28)

    return {'do_locatario': do_locatario, 'do_imovel': do_imovel, 'data_entrada': data_entrada,
            'duracao': duracao, 'valor_mensal': valor_mensal, 'dia_vencimento': dia_vencimento}


def locatarios_ficticios():
    nome = fake.name()
    rg = randrange(1000000, 9999999)
    cpf = randrange(10000000000, 99999999999)
    ocupacao = fake.catch_phrase()
    endereco_completo = fake.address()
    telefone1 = f'{91}98{randrange(1000000, 9999999)}'
    telefone2 = fake.msisdn()[-11::]
    email = fake.email()
    nacionalidade = 'Brasileiro'
    estadocivil = randrange(0, 4)

    return {'nome': nome, 'RG': rg, 'CPF': cpf, 'ocupacao': ocupacao, 'telefone1': telefone1,
            'telefone2': telefone2, 'email': email, 'nacionalidade': nacionalidade, 'estadocivil': estadocivil,
            'endereco_completo': endereco_completo}


def imov_grupo_fict():
    lista = ['Res.', 'Edf.', 'Conj.', 'Rua', 'Avenida', 'Bairro']
    siglas = choice(lista)
    nome = f'{siglas} {fake.bairro()}'

    return {'nome': nome}


def imoveis_ficticios(usuario):
    names = Imovei.objects.filter(do_locador=usuario).values_list('nome', flat=True)
    while True:
        nome = fake.neighborhood()
        if nome not in names:
            break
    cep = randrange(10000000, 99999999)
    endereco = fake.street_name()
    numero = fake.building_number()
    complemento = fake.neighborhood()
    bairro = fake.bairro()
    cidade = fake.city()
    estado = estados[randrange(0, 27)][0]
    uc_energia = randrange(100000000, 999999999)
    uc_agua = randrange(100000000, 999999999)
    grupos_disponiveis = ImovGrupo.objects.all()
    grupo = choice(grupos_disponiveis)
    data_registro = fake.date_time_between_dates(datetime.now() + timedelta(days=-410),
                                                 datetime.now() + timedelta(days=-390))

    return {'nome': nome, 'cep': cep, 'numero': numero, 'complemento': complemento, 'bairro': bairro, 'cidade': cidade,
            'estado': estado, 'endereco': endereco, 'uc_energia': uc_energia, 'uc_agua': uc_agua, 'grupo': grupo,
            'data_registro': data_registro}


def pagamentos_ficticios():
    contratos = Contrato.objects.all()
    contrato_escolhido = choice(contratos)

    ao_contrato = contrato_escolhido
    valor_mensal = int(contrato_escolhido.valor_mensal)
    chance_aleatoria = randrange(valor_mensal // 3, valor_mensal)
    zero_a_cem = randrange(0, 100)
    probabilidade_percentual = 75
    valor_pago = valor_mensal if zero_a_cem <= probabilidade_percentual else chance_aleatoria

    entrada = contrato_escolhido.data_entrada
    data_pagamento = fake.date_between(entrada, datetime.today())

    pix_vista = randrange(0, 1)
    todas = randrange(0, 4)

    forma = choice([pix_vista, pix_vista, todas])
    recibo = choice([True, False])

    return {'ao_contrato': ao_contrato, 'valor_pago': valor_pago, 'data_pagamento': data_pagamento, 'forma': forma,
            'recibo': recibo}


def gastos_ficticios():
    imoveis = Imovei.objects.all()
    do_imovel = choice(imoveis)
    valor = randrange(5000, 28000)
    data = fake.date_between(do_imovel.data_registro.date(), datetime.today())
    observacoes = fake.paragraph(nb_sentences=randrange(1, 5))

    return {'do_imovel': do_imovel, 'valor': valor, 'data': data, 'observacoes': observacoes}


def anotacoes_ficticias():
    titulo = fake.paragraph(nb_sentences=1)
    data_registro = fake.date_between(datetime.today() + timedelta(days=-80), datetime.today())
    texto = fake.paragraph(nb_sentences=randrange(6, 7))
    zero_a_cem = randrange(0, 100)
    probabilidade_percentual = 25
    tarefa = True if zero_a_cem <= probabilidade_percentual else False
    feito = False
    if tarefa:
        probabilidade_percentual = 65
        feito = True if zero_a_cem <= probabilidade_percentual else False

    return {'titulo': titulo, 'data_registro': data_registro, 'texto': texto, 'tarefa': tarefa, 'feito': feito}


def sugestoes_ficticias():
    usuarios = Usuario.objects.all()
    do_usuario = choice(usuarios)
    corpo = fake.paragraph(nb_sentences=randrange(6, 7))

    alguns_usuarios = []
    count = 0
    valor = randrange(0, len(usuarios))
    while True:
        alguns_usuarios.append(choice(usuarios))
        if count == valor:
            break
        count += 1
    likes = alguns_usuarios

    zero_a_cem = randrange(0, 100)
    probabilidade_percentual = 75
    aprovada = True if zero_a_cem <= probabilidade_percentual else False
    implementada = False
    if aprovada:
        probabilidade_percentual = 45
        implementada = True if zero_a_cem <= probabilidade_percentual else False

    dias = randrange(1, 100)
    data_implementada = fake.date_between(datetime.now().date() + timedelta(days=-dias * 2),
                                          datetime.now().date() + timedelta(days=-dias))

    return {'do_usuario': do_usuario, 'corpo': corpo, 'likes': likes, 'aprovada': aprovada,
            'implementada': implementada, 'data_implementada': data_implementada}


def usuarios_ficticios():
    username = fake.user_name()
    password = 'Fb452651'
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.ascii_email()
    telefone = fake.msisdn()[-11::]
    rg = randrange(1000000, 9999999)
    cpf = randrange(10000000000, 99999999999)

    return {'username': username, 'password': password, 'first_name': first_name, 'last_name': last_name,
            'email': email, 'telefone': telefone, 'RG': rg, 'CPF': cpf}
