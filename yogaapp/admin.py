from django.contrib import admin
from .models import BookModel, PlanModel, SettingPlanModel

admin.site.register(BookModel)
admin.site.register(PlanModel)
admin.site.register(SettingPlanModel)