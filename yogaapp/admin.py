from django.contrib import admin
from .models import BookModel, PlanModel, SettingPlanModel, NoteModel, WeekdayDefaultModel

admin.site.register(BookModel)
admin.site.register(PlanModel)
admin.site.register(SettingPlanModel)
admin.site.register(NoteModel)
admin.site.register(WeekdayDefaultModel)