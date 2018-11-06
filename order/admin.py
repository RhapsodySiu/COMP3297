from django.contrib import admin
from .models import MedicalSupply, Order, OrderContent, Type, Clinic, Hospital, Group, DistanceClinic, DistanceClinicHospital

admin.site.register(MedicalSupply)
admin.site.register(Type)
admin.site.register(Group)
admin.site.register(Hospital)
admin.site.register(Clinic)
admin.site.register(DistanceClinic)
admin.site.register(DistanceClinicHospital)

class OrderContentInline(admin.TabularInline):
    model = OrderContent
    raw_id_fields = ['medical_supply']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_by', 'clinic', 'priority', 'order_time', 'processed_time', 'dispatched_time', 'delivered_time']
    list_filter = ['order_time', 'processed_time', 'dispatched_time', 'delivered_time']
    inlines = [OrderContentInline]