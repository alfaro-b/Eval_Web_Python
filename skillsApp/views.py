from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.views import generic
from django.views.decorators.http import require_GET, require_POST
from django.http import HttpRequest, HttpResponse
from typing import Any  # Type utilisé lorsque plusieurs types de valeurs sont possibles
from django.db.models import QuerySet

from .forms import SkillForm, ActivityForm
from .models import Skill, Activity, TimeSlot


class IndexView(generic.ListView):
    """Affiche les compétences et les prochains échanges programmés."""

    model = Skill
    template_name = "skillsApp/index.html"
    context_object_name = "skills"

    # Ajoute des données au contexte envoyé au template HTML.
    # Le contexte est un dictionnaire contenant les données à afficher.
    # **kwargs: Any accepte des arguments supplémentaires de différents types.
    # dict[str, Any] indique que la méthode retourne un dictionnaire avec des clés str et des valeurs de types variés.
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        # Récupération du contexte déjà préparé par la ListView
        context = super().get_context_data(**kwargs)

        # Ajout des prochains créneaux confirmés au contexte
        context["upcoming_slots"] = TimeSlot.objects.filter(
            date__gte=timezone.localdate(),
            helper__isnull=False
        ).order_by("date")

        return context


def choose_skill(request: HttpRequest) -> HttpResponse:
    """ Permet à un utilisateur connecté de choisir ses compétences """

    # Redirection vers l'accueil si l'utilisateur n'est pas connecté
    if not request.user.is_authenticated:
        return redirect("skillsApp:index")

    if request.method == "POST":
        # Formulaire lié aux données envoyées par l'utilisateur
        form = SkillForm(request.POST)

        if form.is_valid():

            # Compétences sélectionnées dans le formulaire
            selected_skills = form.cleaned_data["skill"]

            # Enregistrement des compétences de l'utilisateur
            for skill in Skill.objects.all():
                if skill in selected_skills:
                    skill.users.add(request.user)
                else:
                    skill.users.remove(request.user)
            return redirect("skillsApp:confirm_choice")

    else:
        # Récupération des compétences déjà proposées par l'utilisateur
        user_skills = Skill.objects.filter(users=request.user)
        # Préremplissage du formulaire
        form = SkillForm(initial={"skill": user_skills})

    return render(request, "skillsApp/choose_skill.html", {"form": form})


@require_GET
def confirm_choice(request: HttpRequest) -> HttpResponse:
    """ Page de confirmation d'ajout de compétences """
    return render(request, "skillsApp/confirm_choice.html")


@transaction.atomic
def create_activity(request: HttpRequest) -> HttpResponse:
    """ Permet à l'utilisateur connecté de créer une demande d'aide """

    # Redirection vers l'accueil si l'utilisateur n'est pas connecté
    if not request.user.is_authenticated:
        return redirect("skillsApp:index")

    if request.method == "POST":
        # Formulaire lié aux données envoyées par l'utilisateur
        form = ActivityForm(request.POST)

        if form.is_valid():
            # Création de l'activité sans l'enregistrer immédiatement
            activity = form.save(commit=False)
            # Association de l'activité à l'utilisateur connecté
            activity.requester = request.user
            # Enregistrement de l'activité dans la BDD
            activity.save()

            # Création des créneaux associés à l'activité
            slots = request.POST.getlist("dates")
            for slot in slots:
                if slot:
                    TimeSlot.objects.create(
                        date=slot,
                        activity=activity,
                    )

            # Retour à l'accueil après l'enregistrement
            return redirect("skillsApp:confirm_activity")
    else:
        # Affichage d'un formulaire vide lors de l'accès à la page
        form = ActivityForm()
    return render(request, "skillsApp/create_activity.html", {"form": form})


@require_GET
def confirm_activity(request: HttpRequest) -> HttpResponse:
    """ Page de confirmation de création d'une activité. """
    return render(request, "skillsApp/confirm_activity.html")


@require_GET
def activities_available(request: HttpRequest) -> HttpResponse:
    """ Affiche les activités pour lesquelles l'utilisateur peut proposer son aide."""

    # Redirection vers l'accueil si l'utilisateur n'est pas connecté
    if not request.user.is_authenticated:
        return redirect("skillsApp:index")

    # Récupération des compétences proposées par l'utilisateur
    user_skills = Skill.objects.filter(users=request.user)

    # Recherche des activités disponibles correspondant à ses compétences
    activities = Activity.objects.filter(
        available=True,
        skill__in=user_skills,
        timeslot__date__gte=timezone.localdate(),
        timeslot__helper__isnull=True
    ).exclude(
        requester=request.user
    ).distinct()

    return render(request,
                  "skillsApp/activities_available.html",
                  {"activities": activities}
                  )


class ActivityDetailView(LoginRequiredMixin, generic.DetailView):
    """ Affiche le détail d'une activité et ses créneaux disponibles."""
    login_url = "/skillsApp/login/"

    model = Activity
    template_name = "skillsApp/activity_detail.html"
    context_object_name = "activity"

    # Limite les activités récupérées aux activités encore disponibles.
    # QuerySet[Activity] indique que la méthode retourne un ensemble d'objets Activity provenant de la BDD.
    def get_queryset(self) -> QuerySet[Activity]:
        # Récupération des activités encore disponibles
        return Activity.objects.filter(available=True)

    # Complète le contexte de l'activité avec ses créneaux disponibles.
    # Le dictionnaire retourné contient les données transmises au template.
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Récupération des créneaux futurs sans volontaire
        context["slots"] = TimeSlot.objects.filter(
            activity=self.object,
            date__gte=timezone.localdate(),
            helper__isnull=True
        ).order_by("date")

        return context


@require_POST
def offer_help(request: HttpRequest, pk: int) -> HttpResponse:
    """ Traite la proposition d'aide d'un utilisateur"""

    # Redirection vers l'accueil si l'utilisateur n'est pas connecté
    if not request.user.is_authenticated:
        return redirect("skillsApp:index")

    activity = get_object_or_404(Activity, pk=pk)

    slot_id = request.POST.get("slot")
    # Vérification qu'un créneau a bien été sélectionné
    if slot_id is None:
        return redirect("skillsApp:activities_available")

    selected_slot = get_object_or_404(TimeSlot, pk=slot_id, activity=activity)

    # Vérification des compétences de l'utilisateur
    if not activity.skill.users.filter(pk=request.user.pk).exists():
        return redirect("skillsApp:activities_available")

    # Vérification que l'utilisateur n'est pas le demandeur
    if activity.requester == request.user:
        return redirect("skillsApp:activities_available")

    # Vérification de la disponibilité de l'activité
    if not activity.available:
        return redirect("skillsApp:activities_available")

    # Vérification de la disponibilité du créneau
    if selected_slot.helper is not None or selected_slot.date < timezone.localdate():
        return redirect("skillsApp:activities_available")

    # Vérification qu'aucun autre créneau n'a été accepté
    if TimeSlot.objects.filter(activity=activity, helper__isnull=False).exists():
        return redirect("skillsApp:activities_available")

    # Enregistrement en base avec transaction.atomic pour sécuriser bloc (les deux save s'enregistrent ou aucun si pb)
    with transaction.atomic():
        # Suppression des créneaux non retenus
        TimeSlot.objects.filter(activity=activity).exclude(pk=slot_id).delete()

        # Enregistrement du volontaire
        selected_slot.helper = request.user
        selected_slot.save()

        # L'activité devient indisponible
        activity.available = False
        activity.save()

    return redirect("skillsApp:confirm_help")


@require_GET
def confirm_help(request: HttpRequest) -> HttpResponse:
    """ Page de confirmation de proposition d'aide. """
    return render(request, "skillsApp/confirm_help.html")


class DashboardView(LoginRequiredMixin, generic.TemplateView):
    """ Affiche les demandes et les offres d'aide d'un utilisateur connecté"""
    login_url = "/skillsApp/login/"
    template_name = "skillsApp/dashboard.html"

    # Complète le contexte avec les demandes d'aide, les engagements et les compétences de l'utilisateur connecté.
    # Le dictionnaire retourné contient les données envoyées au tableau de bord.
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Vérification du type de l'utilisateur pour mypy
        assert self.request.user.is_authenticated

        context["activities"] = Activity.objects.filter(requester=self.request.user)

        context["timeslots"] = TimeSlot.objects.filter(
            helper=self.request.user,
            date__gte=timezone.localdate()).order_by("date")

        context["skills"] = Skill.objects.filter(users=self.request.user)

        return context
