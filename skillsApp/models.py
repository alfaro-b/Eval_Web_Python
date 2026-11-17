from django.conf import settings
from django.db import models


class Skill(models.Model):
    """Représente une compétence pouvant être proposée par des utilisateurs."""

    name = models.CharField(max_length=100)

    # Compétences proposées par les utilisateurs
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def __str__(self):
        return self.name


class Activity(models.Model):
    """Représente une demande d'aide créée par un utilisateur."""

    title = models.CharField(max_length=200)
    description = models.TextField()
    available = models.BooleanField(default=True)

    # Utilisateur qui demande de l'aide
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Compétence nécessaire pour l'activité
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class TimeSlot(models.Model):
    """Représente une date proposée pour une activité nécessitant de l'aide."""

    date = models.DateField()

    # Activité associée au créneau
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)

    # Utilisateur qui apporte son aide
    helper = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.activity.title} - {self.date}"
