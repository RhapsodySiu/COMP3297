from django.contrib import admin
from .models import MedicalSupplies, Order, OrderContent, Type

admin.site.register(MedicalSupplies)
admin.site.register(Type)
admin.site.register(Order)
admin.site.register(OrderContent)