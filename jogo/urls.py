from django.urls import path

from jogo import views

app_name = "jogo"

urlpatterns = [
    path("", views.delegacia, name="delegacia"),
    path("cena/", views.cena, name="cena"),
    path("fim/", views.fim, name="fim"),
    path("api/query/", views.api_query, name="api_query"),
    path("api/pistas/", views.api_pistas, name="api_pistas"),
    path("api/dica/", views.api_dica, name="api_dica"),
    path("api/acusacao/", views.api_acusacao, name="api_acusacao"),
    path("api/reset/", views.api_reset, name="api_reset"),
]
