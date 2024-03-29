import uuid
from django.db import models
from django.conf import settings
from enumfields import EnumIntegerField
from enumfields import Enum

import os

# Define image path
def get_image_path(instance, filename):
    return os.path.join('supplies', str(instance.id), filename)

class Type(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class MedicalSupply(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.ForeignKey(Type, related_name='supply', on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    img = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    class Meta:
        verbose_name_plural = "medical supplies"
        ordering = ('description',)
    def __str__(self):
        return self.type.name + ": " + self.description

class Location(models.Model):
    name = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=10, decimal_places=6)
    longitude = models.DecimalField(max_digits=10, decimal_places=6)
    altitude  = models.DecimalField(max_digits=5, decimal_places=2)
    class Meta:
        abstract = True
    def __str__(self):
        return self.name

class Clinic(Location):
    def __str__(self):
        return self.name

class Hospital(Location):
    def __str__(self):
        return self.name

class DistanceClinic(models.Model):
    a = models.ForeignKey(Clinic, related_name="clinicA", on_delete=models.CASCADE)
    b = models.ForeignKey(Clinic, related_name="clinicB", on_delete=models.CASCADE)
    distance = models.DecimalField(max_digits=5, decimal_places=2)
    class Meta:
        unique_together = (("a", "b"),)
    def __str__(self):
        return str(self.distance) + "km" + ": " + self.a.name + " and " + self.b.name 

class DistanceClinicHospital(models.Model):
    a = models.ForeignKey(Hospital, related_name="hospital", on_delete=models.CASCADE)
    b = models.ForeignKey(Clinic, related_name="clinic", on_delete=models.CASCADE)
    distance = models.DecimalField(max_digits=5, decimal_places=2)
    class Meta:
        unique_together = (("a", "b"),)
    def __str__(self):
        return str(self.distance) + "m" + ": " + self.a.name + " and " + self.b.name 

# enum field, in filter: m = MyModel.objects.filter(priority=priority.HIGH), in form: priority = EnumIntegerField(...).formField()
class Priority(Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3

class Status(Enum):
    order = 1
    processing = 2
    processed = 3
    dispatched = 4
    delivered = 5
    class Labels:
        order = 'Queued for processing'
        processing = 'Processing by warehouse'
        processed = 'Queued for dispatch'
        dispatch = 'Dispatch'
        delivered = 'Delivered'

class Order(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    order_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None)
    priority = EnumIntegerField(Priority, default= 3)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, default=None)
    order_time = models.DateTimeField(auto_now_add=True, blank=True)
    processing_time = models.DateTimeField(null=True, blank=True)
    processed_time = models.DateTimeField(null=True, blank=True)
    dispatched_time = models.DateTimeField(null=True, blank=True)
    delivered_time = models.DateTimeField(null=True, blank=True)
    status = EnumIntegerField(Status, default = 1)
    class Meta:
        ordering = ('priority','order_time')
    def __str__(self):
        return 'Order {}'.format(self.id)
    def get_item_no(self):
        return len(self.items.all())
    def get_total_weight(self):
        return round(float(sum(item.get_weight() for item in self.items.all())) + 1.2, 2)

class OrderContent(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    medical_supply = models.ForeignKey(MedicalSupply, related_name='order_items', on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    def __str__(self):
        return '{}'.format(self.id)
    def get_weight(self):
        return self.weight * self.quantity

class Group(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name