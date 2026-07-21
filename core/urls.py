from django.urls import path

from .views import about, contact, faq, home, page_detail

app_name = "core"

urlpatterns = [
    path("", home, name="home"),
    path("a-propos/", about, name="about"),
    path("contact/", contact, name="contact"),
    path("faq/", faq, name="faq"),
    path("pages/<slug:slug>/", page_detail, name="page_detail"),
]
