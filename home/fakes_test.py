from datetime import datetime, timedelta

from faker import Faker
from random import randrange, choice
from home.models import ImovGrupo, Locatario, Imovei, Contrato

locales = 'pt_BR'
fake = Faker(locales)


def contratos_ficticios(request, locador):
    todos_locatarios = Locatario.objects.sem_imoveis().filter(do_locador=locador)
    do_locatario = choice(todos_locatarios)

    todos_imoveis = Imovei.objects.disponiveis().filter(do_locador=locador)
    do_imovel = choice(todos_imoveis)

    data_entrada = fake.date_between(datetime.now().date() + timedelta(days=-215),
                                     datetime.now().date() + timedelta(days=-145))

    duracao = choice([6, 12])

    valor_mensal = randrange(99999, 199999)
    dia_vencimento = randrange(1, 28)

    return {'do_locatario': do_locatario, 'do_imovel': do_imovel, 'data_entrada': data_entrada,
            'duracao': duracao, 'valor_mensal': valor_mensal, 'dia_vencimento': dia_vencimento}


def locatarios_ficticios():
    nome = fake.name()
    rg = randrange(1000000, 9999999)
    cpf = randrange(10000000000, 99999999999)
    ocupacao = fake.catch_phrase()
    telefone1 = fake.msisdn()[-11::]
    telefone2 = fake.msisdn()[-11::]
    email = fake.email()
    nacionalidade = 'Brasileiro'
    estadocivil = randrange(0, 4)

    return {'nome': nome, 'RG': rg, 'CPF': cpf, 'ocupacao': ocupacao, 'telefone1': telefone1,
            'telefone2': telefone2, 'email': email, 'nacionalidade': nacionalidade, 'estadocivil': estadocivil}


def imov_grupo_fict():
    lista = ['Res.', 'Edf.', 'Conj.', 'Rua', 'Avenida', 'Bairro']
    siglas = choice(lista)
    nome = f'{siglas} {fake.bairro()}'

    return {'nome': nome}


def imoveis_ficticios():
    nome = fake.neighborhood()
    cep = fake.postcode()
    endereco = fake.street_address()
    numero = fake.building_number()
    complemento = fake.street_name()
    bairro = fake.bairro()
    cidade = fake.city()
    estado = fake.administrative_unit()
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
    valor_pago = choice([valor_mensal, valor_mensal, chance_aleatoria])

    entrada = contrato_escolhido.data_entrada
    saida = contrato_escolhido.data_saida
    data_pagamento = fake.date_between(entrada, saida())

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

    return {'titulo': titulo, 'data_registro': data_registro, 'texto': texto}


def usuarios_ficticios():
    username = fake.user_name()
    password = 'Fb452651'
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.ascii_email()
    telefone = fake.msisdn()[-11::]

    return {'username': username, 'password': password, 'first_name': first_name, 'last_name': last_name,
            'email': email, 'telefone': telefone}
