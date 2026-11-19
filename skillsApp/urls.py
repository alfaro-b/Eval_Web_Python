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
    path("choose_skill/", views.choose_skill, name="choose_skill"),
    path("confirm_choice/", views.confirm_choice, name="confirm_choice"),
    path("create_activity/", views.create_activity, name="create_activity"),
    path("confirm_activity/", views.confirm_activity, name="confirm_activity"),
    path("activities_available/", views.activities_available, name="activities_available"),
    path("activity/<int:pk>/", views.ActivityDetailView.as_view(), name="activity_detail"),
    path("activity/<int:pk>/offer_help/", views.offer_help, name="offer_help"),
    path("confirm_help/", views.confirm_help, name="confirm_help"),
]
