from django.contrib import admin
from .models import BookModel, PlanModel, SettingPlanModel, NoteModel

admin.site.register(BookModel)
admin.site.register(PlanModel)
admin.site.register(SettingPlanModel)
admin.site.register(NoteModel)