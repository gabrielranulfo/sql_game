# Caso Âmbar — o jogo do SQL

Jogo de investigação criminal feito em **Django**, no qual você é o detetive
**Ícaro Bastos** e só consegue descobrir quem matou a galerista **Helena Vilar**
consultando um banco SQLite **apenas com SQL**.

O limite é a regra do jogo: `SELECT` (e `WITH`) somente — nada de escrever,
apagar ou adulterar a base do inquérito.

---

## Como jogar

1. **Cena do crime** (`/cena/`) — escritório da Galeria Âmbar com hotspots
   clicáveis (escrivaninha, cofre, giz, câmera, janela…). Cada ponto abre a
   narrativa e o botão **“Pesquisar no banco (SQL)”**.
2. **Delegacia** (`/`) — clique no **computador** para abrir o terminal SQL,
   no **telefone** para pedir uma dica ao escrivão e na **porta** para registrar
   a acusação (liberada só com as 6 pistas no caderno).
3. **Terminal SQL** — `Ctrl+Enter` executa, mostra tabela de resultados, esquema
   do banco clicável, histórico das últimas consultas e as pistas desbloqueadas.
4. **Acusação** — dupla confirmação (“não tem volta”) e página final:
   **prisão** (vitória) ou **fuga/arquivamento** (derrota). Em ambos os casos o
   inquérito é encerrado e **todas as pistas são zeradas** para um novo caso.

### Cadeia de 6 pistas

| # | Pista | Tabela | Consulta sugerida | O que desbloqueia |
|---|-------|--------|-------------------|-------------------|
| 1 | Hora exata do crime | `evidencias` | `SELECT * FROM evidencias;` | óbito às **22:14** |
| 2 | O carro que fugiu | `cameras` | `SELECT * FROM cameras WHERE hora BETWEEN '22:00' AND '23:00';` | placa **QRT-4821** |
| 3 | De quem é o carro | `veiculos` | `SELECT * FROM veiculos WHERE placa = 'QRT-4821';` | dono = **pessoa 17** |
| 4 | O suspeito e o álibi | `pessoas` / `depoimentos` | `SELECT * FROM pessoas WHERE id = 17;` | **Miguel Duarte** + álibi do cinema |
| 5 | O álibi desmorona | `ligacoes` | `SELECT * FROM ligacoes WHERE remetente_id = 17 OR receptor_id = 17;` | ligação das **23:40** |
| 6 | O motivo | `transacoes` | `SELECT SUM(valor) FROM transacoes WHERE pessoa_id = 17;` | desvio de **R$ 180.000** |

**Gabarito:** Miguel Duarte · ligação de 23:40 · desvio do seguro de R$ 180.000.

> Cada pista tem *gate*: só é avaliada depois que a anterior foi descoberta.
> A validação é generosa — qualquer consulta honesta que traga o dado-chave
> na tabela certa vale.

---

## Requisitos

- Python **3.14** (Django 6.1 suporta 3.12–3.14)
- Django **6.1.2** (única dependência)

## Instalação

```bash
git clone <seu-repositorio> sql_game
cd sql_game

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_caso       # gera caso/caso.db (idempotente; opcional: o
                                 # banco já é criado automaticamente se faltar)
python manage.py runserver
```

Abra <http://127.0.0.1:8000/> (a porta pode mudar; use `--porta` em
`runserver 0.0.0.0:8770` se a 8000 estiver ocupada).

## Testes

```bash
python manage.py test
python manage.py check
```

A suíte cobre o seed, os 6 tokens da cadeia, o bloqueio de escrita no SQL
(`UPDATE`, `DELETE`, `DROP`, `PRAGMA`, multi-statement, `load_extension`),
a dupla confirmação da acusação, os dois finais e o zerar das pistas.

---

## Estrutura do projeto

```
sql_game/
├── manage.py
├── requirements.txt
├── .gitignore
├── README.md
├── config/                    # settings, urls
│   ├── settings.py            # CASO_DB, app 'jogo', pt-br
│   └── urls.py
├── caso/                      # banco do caso (gerado, fora do git)
│   └── caso.db
└── jogo/
    ├── apps.py                # seed automático se caso.db faltar
    ├── models.py              # sem ORM: progresso vive na sessão
    ├── views.py               # cenas, API de query/pistas/dica/acusação/fim
    ├── urls.py
    ├── tests.py               # 16 testes
    ├── services/
    │   ├── caso.py            # schema, seed determinístico, PISTAS, GABARITO
    │   └── sql_engine.py      # validação + execução somente leitura
    ├── management/commands/seed_caso.py
    ├── templates/jogo/        # base, cena, delegacia, fim
    └── static/jogo/           # css/style.css, js/terminal.js
```

## Arquitetura

- **Dois bancos**: o Django usa `db.sqlite3` apenas para a sessão do jogador;
  o inquérito vive em `caso/caso.db`, aberto por um módulo próprio.
- **Segurança do SQL** (`jogo/services/sql_engine.py`):
  - URI `file:...?mode=ro` (banco só de leitura);
  - `sqlite3.set_authorizer` negando qualquer ação além de `SELECT`/`READ`/`FUNCTION`
    (bloqueia `INSERT/UPDATE/DELETE/PRAGMA/load_extension` na raiz);
  - apenas **um statement** por vez (rejeita `;` extras) e a consulta precisa
    começar com `SELECT` ou `WITH` (após remover comentários);
  - timeout de 3s e retorno limitado a **100 linhas**.
- **Progresso em sessão** (`pistas`, `historico`, `dicas_vistas`, `veredicto`) —
  sem login; `POST /api/reset/` zera tudo.

## Endpoints

| Método | Rota | Função |
|--------|------|--------|
| GET | `/` | delegacia (cena clicável) |
| GET | `/cena/` | cena do crime |
| GET | `/fim/` | página final (prisão/fuga) |
| POST | `/api/query/` | executa `{sql}` e avalia as pistas |
| GET | `/api/pistas/` | progresso, pistas e histórico |
| GET | `/api/dica/` | dica progressiva do escrivão |
| POST | `/api/acusacao/` | `{pessoa_id, prova, motivo, confirmado}` |
| POST | `/api/reset/` | zera a sessão |

## Licença

MIT — livre para estudar, jogar e modificar.
