from django.urls import path
from . import views

app_name = "presentations"

urlpatterns = [
    path("", views.home, name="home"),
    path("generate/", views.generate, name="generate"),
    path("preview/", views.preview, name="preview"),
    path("download/", views.download, name="download"),
    path("regenerate/", views.regenerate, name="regenerate"),
]
