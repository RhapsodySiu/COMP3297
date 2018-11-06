from django.db import models
from django.conf import settings

class ClinicManager(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    clinic = models.ForeignKey("order.Clinic", on_delete=models.CASCADE)
