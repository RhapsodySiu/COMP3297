from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['priority']
        # set these values in view
        exclue = ['order_by', 'clinic']