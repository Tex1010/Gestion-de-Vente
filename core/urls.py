from django.urls import path

from .views import about, home

app_name = "core"

urlpatterns = [
    path("", home, name="home"),
    path("a-propos/", about, name="about"),
]
