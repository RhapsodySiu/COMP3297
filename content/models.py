import uuid
from django.db import models

import os

def get_image_path(instance, filename):
    return os.path.join('photos', str(instance.id), filename)

class Type(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class MedicalSupplies(models.Model):
    class Meta:
        verbose_name_plural = "medical supplies"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    img = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    def __str__(self):
        return self.type.name + ": " + self.description

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_time = models.DateTimeField()
    warehouse_proc_time = models.DateTimeField()
    dispatch_queue_time = models.DateTimeField()
    dispatched_time = models.DateTimeField()
    delivered_time = models.DateTimeField()
    def __str__(self):
        return self.id

class OrderContent(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    medical_supplies = models.ManyToManyField(MedicalSupplies)
