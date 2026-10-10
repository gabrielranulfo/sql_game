"""Views do jogo: cenas, terminal SQL, progresso e acusacao."""

import json

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from jogo.services import caso
from jogo.services.sql_engine import SqlError, executar

LIMITE_HISTORICO = 12


def _descobertas(request):
    return set(request.session.get("pistas", []))


def _historico(request):
    return list(request.session.get("historico", []))


def _contexto(request):
    desc = _descobertas(request)
    atual = caso.proxima_pista(desc)
    return {
        "descobertas": sorted(desc),
        "total_pistas": len(caso.PISTAS),
        "progresso": int(100 * len(desc) / len(caso.PISTAS)),
        "proxima_pista": atual,
        "finalizou": caso.todas_liberadas(desc),
        "pistas": caso.PISTAS,
        "schema_doc": caso.SCHEMA_DOC,
        "schema_json": json.dumps(caso.SCHEMA_DOC, ensure_ascii=False),
        "suspeitos": caso.SUSPEITOS,
        "provas": caso.PROVAS,
        "motivos": caso.MOTIVOS,
        "historico": _historico(request)[:5],
    }


def delegacia(request):
    return render(request, "jogo/delegacia.html", _contexto(request))


def cena(request):
    return render(request, "jogo/cena.html", _contexto(request))


@require_POST
def api_query(request):
    try:
        corpo = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Requisicao invalida."}, status=400)

    sql = (corpo.get("sql") or "").strip()
    desc = _descobertas(request)

    try:
        resultado = executar(sql)
    except SqlError as exc:
        return JsonResponse({"ok": False, "error": str(exc), "tipo": exc.tipo})

    novas = caso.avaliar_pistas(sql, resultado["linhas"], desc)
    if novas:
        request.session["pistas"] = sorted(desc)
        request.session.modified = True

    historico = _historico(request)
    historico.insert(0, sql)
    request.session["historico"] = historico[:LIMITE_HISTORICO]
    request.session.modified = True

    resultado["novas_pistas"] = [
        {"n": p["n"], "titulo": p["titulo"], "narrativa": p["narrativa"]} for p in novas
    ]
    resultado["progresso"] = int(100 * len(desc) / len(caso.PISTAS))
    resultado["descobertas"] = sorted(desc)
    resultado["finalizou"] = caso.todas_liberadas(desc)
    return JsonResponse(resultado)


@require_GET
def api_pistas(request):
    desc = _descobertas(request)
    atual = caso.proxima_pista(desc)
    return JsonResponse({
        "descobertas": sorted(desc),
        "total": len(caso.PISTAS),
        "progresso": int(100 * len(desc) / len(caso.PISTAS)),
        "proxima": None if atual is None else {
            "n": atual["n"], "titulo": atual["titulo"], "briefing": atual["briefing"],
        },
        "detalhes": [
            {
                "n": p["n"], "titulo": p["titulo"], "narrativa": p["narrativa"],
                "liberada": p["n"] in desc,
            }
            for p in caso.PISTAS
        ],
        "historico": _historico(request)[:5],
        "finalizou": caso.todas_liberadas(desc),
    })


@require_GET
def api_dica(request):
    desc = _descobertas(request)
    atual = caso.proxima_pista(desc)
    if atual is None:
        return JsonResponse({"ok": True, "dica": "Todas as pistas ja estao no caderno. Hora de acusar."})
    vezes = request.session.get("dicas_vistas", 0)
    indice = min(vezes, len(atual["dicas"]) - 1)
    request.session["dicas_vistas"] = vezes + 1
    request.session.modified = True
    return JsonResponse({
        "ok": True,
        "pista": atual["n"],
        "titulo": atual["titulo"],
        "dica": atual["dicas"][indice],
        "ultima": indice >= len(atual["dicas"]) - 1,
    })


@require_POST
def api_acusacao(request):
    try:
        corpo = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Requisicao invalida."}, status=400)

    desc = _descobertas(request)
    if not caso.todas_liberadas(desc):
        return JsonResponse({
            "ok": False,
            "venceu": False,
            "erro": "Faltam pistas no caderno. Sem provas suficientes, o juiz nao aceita a denuncia.",
        })

    if corpo.get("confirmado") is not True:
        return JsonResponse({
            "ok": False,
            "venceu": False,
            "exige_confirmacao": True,
            "erro": "A acusacao nao tem volta: confirme o encerramento do inquerito antes de prosseguir.",
        })

    pessoa = int(corpo.get("pessoa_id") or 0)
    prova = corpo.get("prova") or ""
    motivo = corpo.get("motivo") or ""
    gab = caso.GABARITO

    acertos = [
        pessoa == gab["pessoa_id"],
        prova == gab["prova"],
        motivo == gab["motivo"],
    ]
    venceu = all(acertos)
    nome = next((s["nome"] for s in caso.SUSPEITOS if s["id"] == pessoa), "desconhecido")
    rotulo_prova = next((p["texto"] for p in caso.PROVAS if p["id"] == prova), prova)
    rotulo_motivo = next((m["texto"] for m in caso.MOTIVOS if m["id"] == motivo), motivo)

    if venceu:
        texto = (
            "AUTO DE PRISAO: Miguel Duarte, gerente da Galeria Ambar, e indiciado pelo "
            "omicidio de Helena Vilar. O carro da fuga (QRT-4821), as ligacoes de 23:40 "
            "com Iris Nogueira e as duas transferencias de R$ 180.000 fecham o caso. "
            "Ficha limpa, detetive: o culpado esta preso."
        )
        desfecho = "prisao"
    elif acertos[0]:
        texto = (
            f"Voce apontou {nome}, certo do culpado, mas as provas nao sustentam a denuncia. "
            "A defesa derruba o pedido de prisao e o caso e arquivado."
        )
        desfecho = "fuga"
    else:
        texto = (
            f"Denuncia contra {nome}: fraca. Sem a cadeia completa de provas, o suspeito "
            "solto e a investigacao encerrada. O verdadeiro culpado some com o dinheiro."
        )
        desfecho = "fuga"

    request.session["veredicto"] = {
        "venceu": venceu,
        "desfecho": desfecho,
        "texto": texto,
        "acertos": sum(acertos),
        "acusado": nome,
        "prova": rotulo_prova,
        "motivo": rotulo_motivo,
    }
    for chave in ("pistas", "historico", "dicas_vistas"):
        request.session.pop(chave, None)
    request.session.modified = True

    return JsonResponse({
        "ok": True,
        "venceu": venceu,
        "texto": texto,
        "acertos": sum(acertos),
        "redirecionar": reverse("jogo:fim"),
    })


def fim(request):
    """Encerra o caso: mostra o desfecho e o inquerito comeca zerado."""
    veredicto = request.session.get("veredicto")
    if not veredicto:
        return redirect("jogo:delegacia")
    contexto = _contexto(request)
    contexto["veredicto"] = veredicto
    return render(request, "jogo/fim.html", contexto)


@require_POST
def api_reset(request):
    request.session.flush()
    return JsonResponse({"ok": True, "redirecionar": reverse("jogo:delegacia")})
