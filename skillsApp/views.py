from django.utils import timezone
from django.views import generic

from .models import Skill, TimeSlot


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
