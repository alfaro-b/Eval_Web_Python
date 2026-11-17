from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = "skillsApp"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    # Page de connexion gérée par Django, avec redirection vers l'accueil
    path("login/", auth_views.LoginView.as_view(template_name="skillsApp/login.html", next_page="skillsApp:index"), name="login"),
    # Déconnexion de l'utilisateur et retour à l'accueil
    path("logout/", auth_views.LogoutView.as_view(next_page="skillsApp:index"), name="logout"),
]
