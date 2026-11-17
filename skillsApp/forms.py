from django import forms

from skillsApp.models import Skill


class SkillForm(forms.Form):
    """ Formulaire de sélections des compétences"""
    skill = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.SelectMultiple,
        label='Compétences proposées',
        required=False,
        )
