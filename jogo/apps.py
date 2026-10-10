import os

from django.apps import AppConfig
from django.conf import settings


class JogoConfig(AppConfig):
    name = 'jogo'

    def ready(self):
        # Garante que o banco do caso exista logo apos o clone (seed automatico).
        if not os.path.exists(str(settings.CASO_DB)):
            from jogo.services import caso
            caso.build(settings.CASO_DB)
