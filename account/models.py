import uuid
from django.db import models
from django.conf import settings
from enumfields import EnumIntegerField
from enumfields import Enum

class ClinicManager(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    clinic = models.ForeignKey("order.Clinic", on_delete=models.CASCADE)
    
class Role(Enum):
    A = 1
    HA = 2
    WP = 3
    CM = 4
    D = 5
    
    class Labels:
        A = "Admin"
        HA = "Hospital Authority"
        WP = "Warehouse Personnel"
        CM = "Clinic Manager"
        D = "Dispatcher"
    
class Token(models.Model):
    token = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    role = EnumIntegerField(Role)
    isUsed = models.BooleanField(default=False)
