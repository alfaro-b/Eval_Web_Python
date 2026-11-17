from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = "skillsApp"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    # Page de connexion gérée par Django, avec redirection vers l'accueil
    path("login/", auth_views.LoginView.as_view(template_name="skillsApp/login.html", next_page="skillsApp:index"), name="login"),
]
