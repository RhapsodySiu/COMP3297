from django.contrib import admin
from .models import ClinicManager

@admin.register(ClinicManager)
class ClinicManagerAdmin(admin.ModelAdmin):
    list_display = ['user', 'clinic']