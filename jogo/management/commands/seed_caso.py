import os

from django.conf import settings
from django.core.management.base import BaseCommand

from jogo.services import caso


class Command(BaseCommand):
    help = "Gera o banco do caso (caso/caso.db) de forma deterministica."

    def add_arguments(self, parser):
        parser.add_argument("--path", default=None, help="Caminho alternativo do banco do caso.")

    def handle(self, *args, **options):
        caminho = options["path"] or str(settings.CASO_DB)
        caso.build(caminho)
        tamanho = os.path.getsize(caminho)
        self.stdout.write(self.style.SUCCESS(
            f"Caso gerado em {caminho} ({tamanho} bytes, 6 pistas, culpado definido)."
        ))
