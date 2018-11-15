from django.contrib import admin
from .models import ClinicManager, Token

@admin.register(ClinicManager)
class ClinicManagerAdmin(admin.ModelAdmin):
    list_display = ['user', 'clinic']

@admin.register(Token)    
class TokenAdmin(admin.ModelAdmin):
    list_display = ['token', 'email', 'role', 'isUsed']