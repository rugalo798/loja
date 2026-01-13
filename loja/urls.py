from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("comprar", views.comprar_view, name="comprar"),
    path("webhook/mp/", views.mp_webhook, name="mp_webhook"),
]