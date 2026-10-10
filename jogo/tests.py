import json
import os
import tempfile

from django.core.management import call_command
from django.test import Client, TestCase, override_settings

from jogo.services import caso, sql_engine

PLAYTHROUGH = [
    "SELECT * FROM evidencias",
    "SELECT * FROM cameras WHERE hora BETWEEN '22:00' AND '23:00' ORDER BY hora",
    "SELECT * FROM veiculos WHERE placa = 'QRT-4821'",
    "SELECT * FROM pessoas WHERE id = 17",
    "SELECT * FROM depoimentos WHERE pessoa_id = 17",
    "SELECT * FROM ligacoes WHERE remetente_id = 17 OR receptor_id = 17 ORDER BY hora",
    "SELECT SUM(valor) FROM transacoes WHERE pessoa_id = 17",
]


class BaseComCaso(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._tmp = tempfile.TemporaryDirectory()
        cls._db_caso = os.path.join(cls._tmp.name, "caso_teste.db")
        caso.build(cls._db_caso)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()
        super().tearDownClass()

    def setUp(self):
        self.client = Client()
        self.ctx = override_settings(CASO_DB=self._db_caso)
        self.ctx.enable()
        self.addCleanup(self.ctx.disable)


class TesteBancoDoCaso(BaseComCaso):
    def test_seed_comando_e_idempotente(self):
        call_command("seed_caso", path=self._db_caso)
        call_command("seed_caso", path=self._db_caso)
        self.assertTrue(os.path.exists(self._db_caso))

    def test_tokens_chave_existem(self):
        casos = [
            ("SELECT descricao FROM evidencias", "22:14"),
            ("SELECT placa_observada FROM cameras", "QRT-4821"),
            ("SELECT pessoa_id FROM veiculos WHERE placa = 'QRT-4821'", "17"),
            ("SELECT nome FROM pessoas WHERE id = 17", "Miguel Duarte"),
            ("SELECT texto FROM depoimentos WHERE pessoa_id = 17", "cinema"),
            ("SELECT hora FROM ligacoes WHERE remetente_id = 17 OR receptor_id = 17", "23:40"),
        ]
        for sql, token in casos:
            r = sql_engine.executar(sql)
            celulas = " ".join(str(v) for linha in r["linhas"] for v in linha).lower()
            self.assertIn(token.lower(), celulas, f"token {token} ausente em {sql}")
        r = sql_engine.executar("SELECT SUM(valor) FROM transacoes WHERE pessoa_id = 17")
        self.assertEqual(int(r["linhas"][0][0]), 180000)

    def test_cadeia_de_pistas_no_matcher(self):
        descobertas = set()
        for sql in PLAYTHROUGH:
            r = sql_engine.executar(sql)
            caso.avaliar_pistas(sql, r["linhas"], descobertas)
        self.assertEqual(sorted(descobertas), [1, 2, 3, 4, 5, 6])


class TesteSegurancaSql(BaseComCaso):
    def test_bloqueios(self):
        bloqueadas = [
            "UPDATE pessoas SET nome = 'x'",
            "DELETE FROM pessoas",
            "DROP TABLE pessoas",
            "PRAGMA journal_mode = DELETE",
            "INSERT INTO pessoas VALUES (99, 'a', 'b', 'c', 'd')",
            "SELECT 1; DROP TABLE pessoas",
            "WITH x AS (SELECT 1) DELETE FROM pessoas",
            "SELECT load_extension('/tmp/evil')",
            "",
        ]
        for sql in bloqueadas:
            with self.assertRaises(sql_engine.SqlError, msg=sql):
                sql_engine.executar(sql)

    def test_select_libera_esquema_e_limita_linhas(self):
        r = sql_engine.executar("SELECT * FROM sqlite_master")
        self.assertTrue(r["ok"])
        linhas = ["|".join(map(str, r2)) for r2 in sql_engine.executar("SELECT * FROM pessoas")["linhas"]]
        self.assertTrue(any("Helena Vilar" in l for l in linhas))
        r = sql_engine.executar("SELECT * FROM pessoas, pessoas AS b")
        self.assertLessEqual(r["total"], 100)


class TesteApiJogo(BaseComCaso):
    def _query(self, sql):
        return self.client.post(
            "/api/query/", data=json.dumps({"sql": sql}), content_type="application/json"
        ).json()

    def _acusar(self, **dados):
        dados.setdefault("confirmado", True)
        return self.client.post(
            "/api/acusacao/", data=json.dumps(dados), content_type="application/json"
        ).json()

    def test_playthrough_completo_e_acusacao_certa(self):
        for sql in PLAYTHROUGH:
            r = self._query(sql)
            self.assertTrue(r["ok"], r)
        self.assertEqual(r["descobertas"], [1, 2, 3, 4, 5, 6])
        self.assertTrue(r["finalizou"])

        r = self._acusar(pessoa_id=17, prova="ligacao_2340", motivo="desvio_seguro")
        self.assertTrue(r["venceu"])
        self.assertEqual(r["redirecionar"], "/fim/")

    def test_acusacao_errada_perde(self):
        for sql in PLAYTHROUGH:
            self._query(sql)
        r = self._acusar(pessoa_id=3, prova="foto_camera", motivo="heranca")
        self.assertFalse(r["venceu"])
        self.assertEqual(r["redirecionar"], "/fim/")

    def test_acusacao_precoce_e_recusada(self):
        r = self._acusar(pessoa_id=17, prova="ligacao_2340", motivo="desvio_seguro")
        self.assertFalse(r["ok"])

    def test_dupla_checagem_e_obrigatoria(self):
        for sql in PLAYTHROUGH:
            self._query(sql)
        r = self._acusar(pessoa_id=17, prova="ligacao_2340",
                         motivo="desvio_seguro", confirmado=False)
        self.assertFalse(r["ok"])
        self.assertTrue(r["exige_confirmacao"])
        self.assertEqual(self.client.get("/fim/").status_code, 302)

    def test_fim_prisao_e_reinicia_pistas(self):
        for sql in PLAYTHROUGH:
            self._query(sql)
        self._acusar(pessoa_id=17, prova="ligacao_2340", motivo="desvio_seguro")

        resp = self.client.get("/fim/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "preso")
        self.assertContains(resp, "todas as pistas foram zeradas")

        p = self.client.get("/api/pistas/").json()
        self.assertEqual(p["descobertas"], [])

        self.client.post("/api/reset/")
        self.assertEqual(self.client.get("/api/pistas/").json()["descobertas"], [])
        self.assertEqual(self.client.get("/fim/").status_code, 302)

    def test_fim_fuga_quando_provas_erradas(self):
        for sql in PLAYTHROUGH:
            self._query(sql)
        self._acusar(pessoa_id=8, prova="depoimento", motivo="vinganca")
        resp = self.client.get("/fim/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "FUGIU")
        self.assertEqual(self.client.get("/api/pistas/").json()["descobertas"], [])

    def test_fim_sem_veredicto_redireciona(self):
        self.assertEqual(self.client.get("/fim/").status_code, 302)

    def test_gate_bloqueia_pista_fora_de_ordem(self):
        r = self._query("SELECT * FROM ligacoes WHERE remetente_id = 17")
        self.assertNotIn(5, r["descobertas"])
        self.assertTrue(r["ok"])

    def test_erro_de_sql_vem_em_portugues(self):
        r = self._query("SELECT * FROM nao_existe")
        self.assertFalse(r["ok"])
        self.assertIn("Tabela inexistente", r["error"])

    def test_dica_e_reset(self):
        dica = self.client.get("/api/dica/").json()
        self.assertIn("dica", dica)
        self.client.post("/api/reset/")
        p = self.client.get("/api/pistas/").json()
        self.assertEqual(p["descobertas"], [])

    def test_cenas_carregam(self):
        for url in ["/", "/cena/"]:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            self.assertContains(resp, "terminal")
