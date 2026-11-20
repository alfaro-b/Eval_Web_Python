from django import forms

from skillsApp.models import Skill, Activity


class SkillForm(forms.Form):
    """ Formulaire de sélections des compétences"""
    skill = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Compétences proposées',
        required=False,
    )


class ActivityForm(forms.ModelForm):
    """ Formulaire de création d'une demande d'aide"""
    # date = forms.DateField(
    #     label='Date proposée',
    #     widget=forms.DateInput(attrs={'type': 'date'})
    # )

    class Meta:
        model = Activity
        fields = ['title', 'description', 'skill']
