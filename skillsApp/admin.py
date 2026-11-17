from django.contrib import admin

from .models import Skill, Activity, TimeSlot

admin.site.register(Skill)
admin.site.register(Activity)
admin.site.register(TimeSlot)

