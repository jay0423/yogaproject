from django.contrib import admin
from .models import BookModel, PlanModel

admin.site.register(BookModel)
admin.site.register(PlanModel)