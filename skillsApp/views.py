from multiprocessing import context

from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.views import generic
from django.views.decorators.http import require_GET, require_POST

from .forms import SkillForm, ActivityForm
from .models import Skill, Activity, TimeSlot


class IndexView(generic.ListView):
    """Affiche les compétences et les prochains échanges programmés."""

    model = Skill
    template_name = "skillsApp/index.html"
    context_object_name = "skills"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Récupération des créneaux confirmés à partir d'aujourd'hui
        context["upcoming_slots"] = TimeSlot.objects.filter(
            date__gte=timezone.localdate(),
            helper__isnull=False
        ).order_by("date")

        return context


def choose_skill(request):
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
        # Création d'un formulaire vide
        form = SkillForm()

    return render(request, "skillsApp/choose_skill.html", {"form": form})


@require_GET
def confirm_choice(request):
    """ Page de confirmation d'ajout de compétences """
    return render(request, "skillsApp/confirm_choice.html")


def create_activity(request):
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

            # Création du créneau associé à l'activité
            TimeSlot.objects.create(
                date=form.cleaned_data["date"],
                activity=activity,
            )
            # Retour à l'accueil après l'enregistrement
            return redirect("skillsApp:confirm_activity")
    else:
        # Affichage d'un formulaire vide lors de l'accès à la page
        form = ActivityForm()
    return render(request, "skillsApp/create_activity.html", {"form": form})


@require_GET
def confirm_activity(request):
    """ Page de confirmation de création d'une activité. """
    return render(request, "skillsApp/confirm_activity.html")


@require_GET
def activities_available(request):
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


class ActivityDetailView(generic.DetailView):
    """ Affiche le détail d'une activité et ses créneaux disponibles."""
    model = Activity
    template_name = "skillsApp/activity_detail.html"
    context_object_name = "activity"

    def get_queryset(self):
        # Récupération des activités encore disponibles
        return Activity.objects.filter(available=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Récupération des créneaux futurs sans volontaire
        context["slots"] = TimeSlot.objects.filter(
            activity=self.object,
            date__gte=timezone.localdate(),
            helper__isnull=True
        ).order_by("date")

        return context


@require_POST
def offer_help(request, pk):
    """ Traite la proposition d'aide d'un utilisateur"""

    # Redirection vers l'accueil si l'utilisateur n'est pas connecté
    if not request.user.is_authenticated:
        return redirect("skillsApp:index")

    activity = get_object_or_404(Activity, pk=pk)
    slot_id = request.POST.get("slot")
    slot = get_object_or_404(TimeSlot, pk=slot_id, activity=activity)

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
    if slot.helper is not None or slot.date < timezone.localdate():
        return redirect("skillsApp:activities_available")

    # Vérification qu'aucun autre créneau n'a été accepté
    if TimeSlot.objects.filter(activity=activity, helper__isnull=False).exists():
        return redirect("skillsApp:activities_available")

    # Enregistrement du volontaire
    slot.helper = request.user
    slot.save()

    # L'activité devient indisponible
    activity.available = False
    activity.save()

    return redirect("skillsApp:index")
