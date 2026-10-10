"""Caso Âmbar: schema, seed determinístico, cadeia de pistas e gabarito."""

import os
import random

SCHEMA = """
CREATE TABLE locais (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL
);
CREATE TABLE pessoas (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    nascimento TEXT,
    profissao TEXT,
    endereco TEXT
);
CREATE TABLE veiculos (
    id INTEGER PRIMARY KEY,
    pessoa_id INTEGER REFERENCES pessoas(id),
    placa TEXT,
    modelo TEXT,
    cor TEXT
);
CREATE TABLE cameras (
    id INTEGER PRIMARY KEY,
    local_id INTEGER REFERENCES locais(id),
    data TEXT,
    hora TEXT,
    placa_observada TEXT,
    descricao TEXT
);
CREATE TABLE ligacoes (
    id INTEGER PRIMARY KEY,
    remetente_id INTEGER REFERENCES pessoas(id),
    receptor_id INTEGER REFERENCES pessoas(id),
    data TEXT,
    hora TEXT,
    duracao_seg INTEGER
);
CREATE TABLE transacoes (
    id INTEGER PRIMARY KEY,
    pessoa_id INTEGER REFERENCES pessoas(id),
    data TEXT,
    valor REAL,
    tipo TEXT,
    descricao TEXT,
    contraparte TEXT
);
CREATE TABLE depoimentos (
    id INTEGER PRIMARY KEY,
    pessoa_id INTEGER REFERENCES pessoas(id),
    data TEXT,
    hora TEXT,
    onde TEXT,
    texto TEXT
);
CREATE TABLE evidencias (
    id INTEGER PRIMARY KEY,
    local_id INTEGER REFERENCES locais(id),
    tipo TEXT,
    descricao TEXT,
    achado_em TEXT
);
"""

SCHEMA_DOC = {
    "locais": "id | nome | tipo  —  lugares do inquérito",
    "pessoas": "id | nome | nascimento | profissao | endereco  —  vitima, suspeitos e testemunhas",
    "veiculos": "id | pessoa_id | placa | modelo | cor  —  dono de cada carro (pessoa_id liga em pessoas)",
    "cameras": "id | local_id | data | hora | placa_observada | descricao  —  registro das cameras de seguranca",
    "ligacoes": "id | remetente_id | receptor_id | data | hora | duracao_seg  —  quem ligou para quem",
    "transacoes": "id | pessoa_id | data | valor | tipo | descricao | contraparte  —  movimentacao financeira",
    "depoimentos": "id | pessoa_id | data | hora | onde | texto  —  testemunhos colhidos pela policia",
    "evidencias": "id | local_id | tipo | descricao | achado_em  —  laudos e achados do local do crime",
}

DATA_CRIME = "2026-10-16"

FIXOS = {
    1: ("Helena Vilar", "1958-03-12", "galerista", "Rua das Palmeiras 210"),
    2: ("Sergio Vilar", "1955-06-30", "corretor de imoveis", "Rua das Palmeiras 210"),
    3: ("Beatriz Vilar", "1986-07-04", "arquiteta", "Av. Ipiranga 770, apto 91"),
    5: ("Renata Salles", "1979-11-22", "advogada", "Rua Aurora 45"),
    8: ("Iris Nogueira", "1981-05-30", "contador", "Rua do Comercio 1200, sala 4"),
    17: ("Miguel Duarte", "1975-01-19", "gerente da galeria", "Rua Aurora 88, apto 32"),
    22: ("Osvaldo Prado", "1969-09-08", "motorista", "Vila Operaria, rua 12, casa 7"),
}

PRENOMES = [
    "Aline", "Bruno", "Carla", "Diego", "Elisa", "Fabio", "Gabriela", "Hugo",
    "Ivone", "Joao", "Karina", "Lucas", "Marina", "Nelson", "Olivia", "Paulo",
    "Queren", "Rafael", "Sonia", "Tiago", "Ursula", "Vitor", "Wanda", "Yara",
    "Zeca", "Amora", "Caio", "Dora",
]
SOBRENOMES = [
    "Andrade", "Barros", "Cavalcanti", "Duarte", "Esteves", "Ferraz", "Gomes",
    "Hollanda", "Iglesias", "Jamile", "Klabin", "Lobo", "Macedo", "Neves",
    "Oliveira", "Peixoto", "Queiroz", "Ramalho", "Tavares", "Urquiza",
    "Vasques", "Wanderley",
]
PROFISSOES = [
    "pedreiro", "professora", "garcom", "analista de sistemas", "florista",
    "taxista", "dentista", "jornalista", "cozinheira", "seguranca",
    "padeiro", "musico", "quimica", "retratista", "barmen",
    "recepcionista", "engenheira", "costureira", "sapateiro", "vendedor",
]
RUAS = [
    "Rua Independencia", "Av. Central", "Rua do Sol", "Travessa das Flores",
    "Rua Bahia", "Av. Brasil", "Rua das Acacias", "Rua do Porto",
    "Alameda Santos", "Rua XV de Novembro",
]

LOCAIS = [
    (1, "Galeria Ambar - escritorio", "cena do crime"),
    (2, "Garagem da Galeria Ambar", "cena do crime"),
    (3, "Avenida Central", "via de fuga"),
    (4, "Posto 24h - Avenida Central", "via de fuga"),
    (5, "Cinema Avenida", "alibi a verificar"),
    (6, "Delegacia do 7o Distrito", "sede do inquerito"),
]

SUSPEITOS = [
    {"id": 3, "nome": "Beatriz Vilar"},
    {"id": 5, "nome": "Renata Salles"},
    {"id": 8, "nome": "Iris Nogueira"},
    {"id": 17, "nome": "Miguel Duarte"},
    {"id": 22, "nome": "Osvaldo Prado"},
]

PROVAS = [
    {"id": "foto_camera", "texto": "A foto da camera da garagem as 22:31"},
    {"id": "ligacao_2340", "texto": "A ligacao de 23:40 entre Miguel e Iris"},
    {"id": "depoimento", "texto": "O depoimento de Osvaldo sobre o horario"},
]

MOTIVOS = [
    {"id": "desvio_seguro", "texto": "O desvio de R$ 180.000 do seguro da galeria"},
    {"id": "heranca", "texto": "A heranca da galeria deixada pela vitima"},
    {"id": "vinganca", "texto": "Uma vinganca antiga por causa de um amor perdido"},
]

GABARITO = {"pessoa_id": 17, "prova": "ligacao_2340", "motivo": "desvio_seguro"}

PISTAS = [
    {
        "n": 1,
        "titulo": "Hora exata do crime",
        "tabelas": ["evidencias"],
        "tokens_any": ["22:14"],
        "tokens_all": [],
        "gate": None,
        "briefing": "O escrivao ainda nao sabe dizer a hora certa. Procure o laudo do corpo no banco do caso.",
        "narrativa": (
            "LAUDO: Helena Vilar foi encontrada sem sinais de vida no escritorio da "
            "Galeria Ambar. Oito as 22:14. A janela critica do crime esta fixada."
        ),
        "dicas": [
            "As informacoes do corpo estao em uma tabela de achados do local: evidencias.",
            "Tente: SELECT * FROM evidencias;",
        ],
    },
    {
        "n": 2,
        "titulo": "O carro que fugiu",
        "tabelas": ["cameras"],
        "tokens_any": ["QRT-4821"],
        "tokens_all": [],
        "gate": 1,
        "briefing": "Entre 22:00 e 23:00 alguma coisa saiu da garagem da galeria. Filtre as cameras nesse intervalo.",
        "narrativa": (
            "Camera da garagem, 22:31: um carro com a placa QRT-4821 acelera em "
            "direcao a Avenida Central. Alguem deixou o local minutos apos o óbito."
        ),
        "dicas": [
            "As horas estao na coluna hora, em formato 22:31 — use BETWEEN.",
            "Tente: SELECT * FROM cameras WHERE hora BETWEEN '22:00' AND '23:00';",
        ],
    },
    {
        "n": 3,
        "titulo": "De quem e o carro",
        "tabelas": ["veiculos"],
        "tokens_any": ["17"],
        "tokens_all": [],
        "gate": 2,
        "briefing": "Ache o registro do veiculo QRT-4821 e descubra o dono (coluna pessoa_id).",
        "narrativa": (
            "QRT-4821 (Fiat Cronos, prata) pertence a pessoa_id 17. "
            "O dono do carro da fuga agora tem um numero."
        ),
        "dicas": [
            "Busque a placa exata na tabela veiculos.",
            "Tente: SELECT * FROM veiculos WHERE placa = 'QRT-4821';",
        ],
    },
    {
        "n": 4,
        "titulo": "O suspeito e o alibi",
        "tabelas": ["pessoas", "depoimentos"],
        "tokens_any": ["miguel duarte", "cinema"],
        "tokens_all": [],
        "gate": 3,
        "briefing": "Quem e a pessoa 17? E o que ela disse a policia na noite seguinte?",
        "narrativa": (
            "Miguel Duarte, 51, gerente da galeria. No depoimento ele jura que estava "
            "no Cinema Avenida com a filha, sessao das 21h. Alibi perfeito... se fosse verdade."
        ),
        "dicas": [
            "SELECT * FROM pessoas WHERE id = 17;",
            "Depois: SELECT * FROM depoimentos WHERE pessoa_id = 17;",
        ],
    },
    {
        "n": 5,
        "titulo": "O alibi desmorona",
        "tabelas": ["ligacoes"],
        "tokens_any": ["23:40"],
        "tokens_all": [],
        "gate": 4,
        "briefing": "Se ele estava no cinema, para quem estava ligando depois da meia-noite? Cruze os telefones dele.",
        "narrativa": (
            "As 22:05 e de novo as 23:40, Miguel ligou para Iris Nogueira, a contadora "
            "da galeria. Nenhuma delas durou o tempo de um filme. O alibi caiu."
        ),
        "dicas": [
            "remetente_id e receptor_id: ele pode ter ligado OU recebido.",
            "Tente: SELECT * FROM ligacoes WHERE remetente_id = 17 OR receptor_id = 17;",
        ],
    },
    {
        "n": 6,
        "titulo": "O motivo (o dinheiro)",
        "tabelas": ["transacoes"],
        "tokens_any": ["180000"],
        "tokens_all": ["100000", "80000"],
        "gate": 5,
        "briefing": "Por que um gerente mataria a chefe? Some o que saiu da conta dele nos dias seguintes.",
        "narrativa": (
            "Duas transferencias de 100.000 e 80.000 para uma conta no exterior, "
            "total de 180.000: exatamente o valor do seguro de vida da galeria. "
            "Motive e prenda."
        ),
        "dicas": [
            "Use agregacao: SELECT SUM(valor) FROM transacoes WHERE pessoa_id = 17;",
            "Ou traga as duas linhas com SELECT * FROM transacoes WHERE pessoa_id = 17;",
        ],
    },
]


def _pessoas():
    linhas = []
    usados = set(FIXOS)
    for pid, (nome, nasc, prof, end) in sorted(FIXOS.items()):
        linhas.append((pid, nome, nasc, prof, end))
    rng = random.Random(7)
    restantes = [i for i in range(1, 41) if i not in usados]
    for pid in restantes:
        nome = f"{rng.choice(PRENOMES)} {rng.choice(SOBRENOMES)}"
        ano = rng.randint(1962, 2001)
        nasc = f"{ano}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}"
        prof = rng.choice(PROFISSOES)
        end = f"{rng.choice(RUAS)}, {rng.randint(1, 2000)}"
        linhas.append((pid, nome, nasc, prof, end))
    return sorted(linhas, key=lambda r: r[0])


def _veiculos():
    rng = random.Random(11)
    modelos = [
        ("Volkswagen Gol", "branco"), ("Chevrolet Onix", "preto"),
        ("Hyundai HB20", "azul"), ("Toyota Corolla", "prata"),
        ("Renault Kwid", "vermelho"), ("Ford Ka", "cinza"),
        ("Fiat Mobi", "branco"), ("Nissan Kicks", "branco"),
        ("Jeep Renegade", "verde"), ("Peugeot 208", "cinza"),
        ("Citroen C3", "azul"),
    ]
    donos = [3, 5, 8, 22, 2, 4, 6, 9, 12, 15, 19]
    linhas = []
    for i, (modelo, cor) in enumerate(modelos, start=1):
        placa = f"{rng.choice('ABCDEFGHJKLMNPRSTUVWXYZ')}{rng.choice('ABCDEFGHJKLMNPRSTUVWXYZ')}{rng.choice('ABCDEFGHJKLMNPRSTUVWXYZ')}-{rng.randint(1000, 9999)}"
        linhas.append((i, donos[i - 1], placa, modelo, cor))
    linhas.append((12, 17, "QRT-4821", "Fiat Cronos", "prata"))
    return linhas


def _cameras():
    rng = random.Random(23)
    placas_decoy = ["QRT-7710", "MKS-2280", "LKP-4413", "BRA-9081", "DXT-3355", "HGF-7126"]
    locais_cam = [1, 2, 3, 4]
    linhas = []
    cid = 0
    for local_id in locais_cam:
        for _ in range(15):
            cid += 1
            hora = f"{rng.randint(18, 23):02d}:{rng.randint(0, 59):02d}"
            if rng.random() < 0.4:
                hora = f"22:{rng.randint(0, 59):02d}"
            placa = rng.choice(placas_decoy)
            desc = rng.choice([
                "movimento capturado, sem ocorrencias",
                "veiculo passa sem parar",
                "imagem parcial por reflexo",
                "pedestre atravessa a cena",
                "veiculo estaciona e segue viagem",
            ])
            linhas.append((cid, local_id, DATA_CRIME, hora, placa, desc))
    linhas.append((cid + 1, 2, DATA_CRIME, "22:31", "QRT-4821",
                   "Fiat Cronos prata sai pela saida lateral e acelera para a Avenida Central"))
    linhas.append((cid + 2, 2, DATA_CRIME, "22:44", "QRT-7710",
                   "Volkswagen Gol branco entra na garagem e estaciona no nivel -1"))
    linhas.append((cid + 3, 3, DATA_CRIME, "23:58", "MKS-2280",
                   "veiculo não identificado trafega em alta velocidade"))
    return linhas


def _ligacoes():
    rng = random.Random(31)
    linhas = [
        (1, 17, 8, DATA_CRIME, "22:05", 96),
        (2, 8, 17, DATA_CRIME, "23:40", 312),
        (3, 17, 3, DATA_CRIME, "21:12", 44),
        (4, 22, 17, "2026-10-15", "19:30", 71),
        (5, 5, 17, "2026-10-16", "18:02", 133),
    ]
    cid = 5
    pessoas = [p[0] for p in _pessoas()]
    for _ in range(35):
        cid += 1
        a, b = rng.sample(pessoas, 2)
        dia = rng.choice([DATA_CRIME, "2026-10-15", "2026-10-17"])
        hora = f"{rng.randint(8, 23):02d}:{rng.randint(0, 59):02d}"
        if hora == "23:40":
            hora = "23:41"
        linhas.append((cid, a, b, dia, hora, rng.randint(8, 480)))
    return linhas


def _transacoes():
    rng = random.Random(43)
    linhas = [
        (1, 17, "2026-10-19", 100000.0, "transferencia",
         "transferencia para conta no exterior - titularidade laranja", "Banco Internacional S.A."),
        (2, 17, "2026-10-21", 80000.0, "transferencia",
         "segunda parcela: pagamento do seguro de vida da Galeria Ambar", "Banco Internacional S.A."),
    ]
    cid = 2
    pessoas = [p[0] for p in _pessoas() if p[0] != 17]
    for _ in range(28):
        cid += 1
        pid = rng.choice(pessoas)
        dia = f"2026-{rng.choice([9, 10]):02d}-{rng.randint(1, 28):02d}"
        valor = float(rng.randint(3, 999) * 10 + rng.choice([0, 5]))
        linhas.append((cid, pid, dia, valor, rng.choice(["deposito", "pix", "saque"]),
                       rng.choice(["pagamento de fornecedor", "salario", "aluguel",
                                   "compra em loja", "transferencia para conjuge"]),
                       rng.choice(["Loja Central", "Imobiliaria Norte", "Pessoa fisica",
                                   "Mercado Bom Preco", "Empresa Delta"])))
    return linhas


def _depoimentos():
    linhas = [
        (1, 17, "2026-10-17", "10:20", "Delegacia do 7o Distrito",
         "Na noite do crime eu estava no Cinema Avenida com minha filha, sessao das 21h. "
         "Nunca passei perto da galeria depois que fui embora as 19h."),
        (2, 3, "2026-10-17", "11:05", "Delegacia do 7o Distrito",
         "Minha mae e eu nao nos falavamos ha meses. Fiquei em casa a noite toda lendo."),
        (3, 8, "2026-10-17", "14:30", "Delegacia do 7o Distrito",
         "Fechei a contabilidade as 18h e fui direto para casa. Nao sei de nada."),
        (4, 22, "2026-10-18", "09:15", "Delegacia do 7o Distrito",
         "Levei a patroa para casa as 21h30 e esperei ela entrar. Depois fui embora, "
         "so vi o Miguel saindo correndo da garagem la pelas 22h30."),
        (5, 5, "2026-10-18", "16:40", "Escritorio Salles Advogados",
         "Helena me ligaria na segunda para revisar o testamento. Nao houve testamento novo."),
    ]
    rng = random.Random(53)
    textos = [
        "Ouvi barulho na rua, mas nao prestei atencao no horario.",
        "Trabalhei o turno inteiro, meus colegas podem confirmar.",
        "Vi uma discussao na porta da galeria na terca passada, nada grave.",
        "Nao tenho nada a declarar sobre a morte da Helena.",
        "A Helena andava assustada nos ultimos tempos, falava em seguro.",
        "Vendi um quadro para ela na semana passada, tudo certinho.",
        "Estava no mercado, tenho a nota fiscal do dia.",
        "Miguel andava muito nervoso depois que a auditoria foi marcada.",
        "Iris nunca saia do escritorio depois das 18h, estranho aquele dia.",
        "O portao da garagem estava aberto quando cheguei de madrugada.",
    ]
    pessoas = [p[0] for p in _pessoas()]
    cid = 5
    for texto in textos:
        cid += 1
        pid = rng.choice(pessoas)
        linhas.append((cid, pid, rng.choice([DATA_CRIME, "2026-10-17", "2026-10-18"]),
                       f"{rng.randint(8, 18):02d}:{rng.randint(0, 59):02d}",
                       rng.choice(["Delegacia do 7o Distrito", "Telefone", "Rua"]),
                       texto))
    return linhas


def _evidencias():
    return [
        (1, 1, "laudo", "Corpo de Helena Vilar encontrado sem sinais de vida no escritorio; "
                        "obito as 22:14, causas em investigacao", "2026-10-16 22:40"),
        (2, 1, "impressao digital", "Impressao parcial na alca do cofre, nao catalogada", "2026-10-16 23:10"),
        (3, 1, "documento", "Contrato de seguro de vida com apolice de R$ 180.000 em nome da vitima",
         "2026-10-17 08:30"),
        (4, 2, "rastro", "Rastos de pneu recentes na saida lateral da garagem", "2026-10-16 23:25"),
        (5, 1, "arma", "Projétil 9mm recolhido sob a escrivaninha", "2026-10-16 23:40"),
        (6, 1, "objeto", "Celular da vitima quebrado no chao, tela trincada", "2026-10-16 22:55"),
        (7, 2, "cftv", "Gravacao da camera da garagem entre 22:00 e 23:00 conferenciada e copiada",
         "2026-10-17 09:00"),
        (8, 5, "relato", "Funcionario do cinema informa que a sessao das 21h nao existia",
         "2026-10-18 11:20"),
        (9, 1, "documento", "Livro-caixa da galeria com tres lancamentos sem conciliacao",
         "2026-10-17 15:00"),
        (10, 6, "relatorio", "Relatorio de telefonia recebido da operadora, 40 chamadas no periodo",
         "2026-10-19 10:00"),
    ]


def build(db_path):
    """(Re)cria o banco do caso de forma deterministica. Idempotente."""
    db_path = str(db_path)
    pasta = os.path.dirname(db_path)
    if pasta:
        os.makedirs(pasta, exist_ok=True)
    if os.path.exists(db_path):
        os.remove(db_path)
    import sqlite3

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA)
        conn.executemany("INSERT INTO locais VALUES (?,?,?)", LOCAIS)
        conn.executemany("INSERT INTO pessoas VALUES (?,?,?,?,?)", _pessoas())
        conn.executemany("INSERT INTO veiculos VALUES (?,?,?,?,?)", _veiculos())
        conn.executemany("INSERT INTO cameras VALUES (?,?,?,?,?,?)", _cameras())
        conn.executemany("INSERT INTO ligacoes VALUES (?,?,?,?,?,?)", _ligacoes())
        conn.executemany("INSERT INTO transacoes VALUES (?,?,?,?,?,?,?)", _transacoes())
        conn.executemany("INSERT INTO depoimentos VALUES (?,?,?,?,?,?)", _depoimentos())
        conn.executemany("INSERT INTO evidencias VALUES (?,?,?,?,?)", _evidencias())
        conn.commit()
    finally:
        conn.close()
    return db_path


def proxima_pista(descobertas):
    """Retorna a proxima pista ainda nao descoberta cujo gate ja foi cumprido."""
    descobertas = set(descobertas)
    for p in PISTAS:
        if p["n"] in descobertas:
            continue
        if p["gate"] is None or p["gate"] in descobertas:
            return p
    return None


def todas_liberadas(descobertas):
    return len(descobertas) >= len(PISTAS)


def _celulas(rows):
    cells = []
    for row in rows:
        for v in row:
            if v is None:
                continue
            if isinstance(v, float) and v.is_integer():
                s = str(int(v))
            else:
                s = str(v)
            cells.append(s)
    return cells


def _bate(token, cells):
    token = str(token).strip().lower()
    for c in cells:
        cl = c.lower()
        if token.isalnum() and token.isdigit():
            if cl == token or cl.startswith(token + "."):
                return True
        elif token in cl:
            return True
    return False


def avaliar_pistas(sql, rows, descobertas):
    """Retorna a lista de pistas recem-desbloqueadas por esta consulta."""
    if not rows:
        return []
    import re

    tabelas = set()
    for m in re.finditer(r"\b(?:from|join)\s+[\"']?([a-zA-Z_][a-zA-Z0-9_]*)[\"']?", sql, re.I):
        tabelas.add(m.group(1).lower())
    if not tabelas:
        return []

    cells = _celulas(rows)
    novas = []
    for p in PISTAS:
        if p["n"] in descobertas:
            continue
        if p["gate"] is not None and p["gate"] not in descobertas:
            continue
        if not tabelas.intersection(p["tabelas"]):
            continue
        ok_any = any(_bate(t, cells) for t in p["tokens_any"]) if p["tokens_any"] else False
        ok_all = all(_bate(t, cells) for t in p["tokens_all"]) if p["tokens_all"] else False
        if p["tokens_any"] and p["tokens_all"]:
            acertou = ok_any or ok_all
        elif p["tokens_any"]:
            acertou = ok_any
        else:
            acertou = ok_all
        if acertou:
            novas.append(p)
            descobertas.add(p["n"])
    return novas
