from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from faker import Faker
from random import randrange, choice

from home.models import ImovGrupo, Locatario, Imovei, Contrato, Usuario, estados

locales = 'pt_BR'
fake = Faker(locales)


def porcentagem_de_chance(percentual):
    zero_a_cem = randrange(0, 100)
    return True if zero_a_cem <= percentual else False


def contratos_ficticios(request, locador):
    todos_locatarios = Locatario.objects.filter(do_locador=locador)
    do_locatario = choice(todos_locatarios)

    todos_imoveis = Imovei.objects.filter(do_locador=locador)
    do_imovel = choice(todos_imoveis)

    count = 0
    while True:
        dias = count + randrange(90, 365)
        passado = fake.date_between(datetime.now().date() - timedelta(days=dias * randrange(2, 5)),
                                     datetime.now().date() - timedelta(days=dias))

        dias = count + randrange(10, 30)
        presente = fake.date_between(datetime.now().date() - timedelta(days=dias * 2),
                                    datetime.now().date() - timedelta(days=dias))
        dias = count + randrange(30, 90)
        futuro = fake.date_between(datetime.now().date() + timedelta(days=dias),
                                    datetime.now().date() + timedelta(days=dias * 2))

        entrada_novo = presente if porcentagem_de_chance(75) else choice([passado, futuro])
        # print(passado.strftime("%d/%m/%Y"), presente.strftime("%d/%m/%Y"), futuro.strftime("%d/%m/%Y"))
        # print('escolhido:', entrada_novo.strftime("%d/%m/%Y"))
        # print('')

        duracao = randrange(3, 18) - count
        if duracao <= 0:
            duracao = 1

        saida_novo = entrada_novo + relativedelta(months=duracao)
        contratos_deste_imovel = Contrato.objects.filter(do_imovel=do_imovel.pk)
        permitido = True

        for contrato in contratos_deste_imovel:
            entrada_antigo = contrato.data_entrada
            saida_antigo = contrato.data_entrada + relativedelta(months=contrato.duracao)

            if entrada_antigo <= entrada_novo <= saida_antigo:
                permitido = False
            if entrada_antigo <= saida_novo <= saida_antigo:
                permitido = False

            if entrada_antigo >= entrada_novo >= saida_antigo:
                permitido = False
            if entrada_antigo >= saida_novo >= saida_antigo:
                permitido = False

            if entrada_antigo >= entrada_novo and saida_antigo <= saida_novo:
                permitido = False

        if permitido is True:
            data_entrada = entrada_novo
            break
        else:
            count += 1

    centavos = '00' if porcentagem_de_chance(70) else randrange(10, 95, step=5)
    reais = [randrange(500, 1200, step=150), randrange(700, 3400, step=180), randrange(750, 3450, step=130),
             randrange(3400, 12000, step=1500), randrange(520, 32460, step=100)]
    valor_mensal = f'{choice(reais)}{centavos}'

    dia_vencimento = randrange(1, 28)
    em_posse = True if porcentagem_de_chance(85) else False

    return {'do_locatario': do_locatario, 'do_imovel': do_imovel, 'data_entrada': data_entrada,
            'duracao': duracao, 'valor_mensal': valor_mensal, 'dia_vencimento': dia_vencimento, 'em_posse': em_posse}


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
    tipo = randrange(0, 7)
    return {'nome': nome, 'tipo': tipo}


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


def pagamentos_ficticios(usuario):
    x = Contrato.objects.filter(do_locador=usuario)
    contratos = []
    for contrato in x:
        if contrato.quitado() is False:
            contratos.append(contrato)

    if len(contratos) > 0:
        contrato_escolhido = choice(contratos)
        ao_contrato = contrato_escolhido
        valor_mensal = int(contrato_escolhido.valor_mensal)
        chance_aleatoria = randrange(valor_mensal // 3, valor_mensal)
        valor_sorteado = valor_mensal if porcentagem_de_chance(75) else chance_aleatoria
        valor_pago = str(valor_sorteado if valor_sorteado < int(contrato_escolhido.falta_pg()) else int(
            contrato_escolhido.falta_pg()))
        data_pagamento = fake.date_between(contrato_escolhido.data_entrada, contrato_escolhido.data_saida())
        pix_vista = randrange(0, 1)
        todas = randrange(0, 4)
        forma = pix_vista if porcentagem_de_chance(65) else todas
        recibo = True if porcentagem_de_chance(60) else False
    else:
        return None

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
    tarefa = True if porcentagem_de_chance(50) else False
    feito = False
    if tarefa:
        feito = True if porcentagem_de_chance(25) else False

    return {'titulo': titulo, 'data_registro': data_registro, 'texto': texto, 'tarefa': tarefa, 'feito': feito}


def sugestoes_ficticias():
    usuarios = Usuario.objects.all()
    do_usuario = choice(usuarios)
    corpo = fake.paragraph(nb_sentences=randrange(6, 7))

    zero_a_cem = randrange(0, 100)
    probabilidade_percentual = 75

    alguns_usuarios = []
    count = 0
    valor = randrange(0, len(usuarios))
    while True:
        alguns_usuarios.append(choice(usuarios)) if zero_a_cem <= probabilidade_percentual else None
        if count == valor:
            break
        count += 1
    likes = alguns_usuarios

    aprovada = True if porcentagem_de_chance(75) else False
    implementada = False
    if aprovada:
        implementada = True if porcentagem_de_chance(45) else False

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
