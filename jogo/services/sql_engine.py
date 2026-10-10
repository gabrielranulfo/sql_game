"""Motor de consulta SQL do jogo: somente SELECT, banco do caso em modo leitura."""

import re
import sqlite3
import time

from django.conf import settings

MAX_ROWS = 100
TIMEOUT = 3.0

_COMENTARIO_LINHA = re.compile(r"--.*?$", re.M)
_COMENTARIO_BLOCO = re.compile(r"/\*.*?\*/", re.S)


class SqlError(Exception):
    """Erro de consulta traduzido para o jogador."""

    def __init__(self, mensagem, tipo="consulta"):
        super().__init__(mensagem)
        self.tipo = tipo


def _limpar(sql):
    sem_coment = _COMENTARIO_BLOCO.sub(" ", sql)
    sem_coment = _COMENTARIO_LINHA.sub(" ", sem_coment)
    return sem_coment.strip()


def validar(sql):
    if not sql or not sql.strip():
        raise SqlError("Digite uma consulta SQL.", tipo="vazia")
    limpo = _limpar(sql)
    if not limpo:
        raise SqlError("Digite uma consulta SQL.", tipo="vazia")
    if ";" in limpo.rstrip(";"):
        raise SqlError("Uma consulta por vez, por favor: remova o ';' extra.", tipo="multipla")
    corpo = limpo.rstrip().rstrip(";").strip()
    if not re.match(r"^(SELECT|WITH)\b", corpo, re.I):
        raise SqlError(
            "Aqui so funciona investigacao com SELECT (ou WITH). Nada de escrever no banco.",
            tipo="permissao",
        )
    return corpo


def _authorizer(acao, arg1, arg2, nome_bd, fonte):
    permitidas = {
        getattr(sqlite3, "SQLITE_SELECT", 21),
        getattr(sqlite3, "SQLITE_READ", 20),
        getattr(sqlite3, "SQLITE_FUNCTION", 31),
        getattr(sqlite3, "SQLITE_RECURSIVE", 33),
    }
    return sqlite3.SQLITE_OK if acao in permitidas else sqlite3.SQLITE_DENY


def _abrir():
    uri = "file:{}?mode=ro".format(settings.CASO_DB)
    conn = sqlite3.connect(uri, uri=True, timeout=TIMEOUT)
    conn.set_authorizer(_authorizer)
    return conn


def executar(sql):
    """Executa uma consulta e retorna um dict pronto para JSON."""
    inicio = time.perf_counter()
    corpo = validar(sql)
    conn = None
    try:
        conn = _abrir()
        cursor = conn.cursor()
        cursor.execute(corpo)
        linhas_brutas = cursor.fetchmany(MAX_ROWS + 1)
        truncado = len(linhas_brutas) > MAX_ROWS
        linhas = linhas_brutas[:MAX_ROWS]
        colunas = [d[0] for d in cursor.description] if cursor.description else []
        elapsed = round((time.perf_counter() - inicio) * 1000, 1)
        return {
            "ok": True,
            "colunas": colunas,
            "linhas": [[_jsonavel(v) for v in r] for r in linhas],
            "total": len(linhas),
            "truncado": truncado,
            "tempo_ms": elapsed,
            "error": None,
        }
    except SqlError:
        raise
    except sqlite3.OperationalError as exc:
        texto = str(exc).lower()
        if "authorization" in texto or "denied" in texto or "not authorized" in texto:
            raise SqlError("Essa operacao nao e permitida: o banco do caso e somente leitura.",
                           tipo="permissao") from exc
        if "no such table" in texto:
            raise SqlError(f"Tabela inexistente: {exc}. Confira o esquema no painel ao lado.",
                           tipo="sintaxe") from exc
        raise SqlError(f"Erro na consulta: {exc}", tipo="sintaxe") from exc
    except sqlite3.Error as exc:
        raise SqlError(f"Erro na consulta: {exc}", tipo="sintaxe") from exc
    finally:
        if conn is not None:
            conn.close()


def _jsonavel(valor):
    if isinstance(valor, bytes):
        return valor.decode("utf-8", "replace")
    return valor
