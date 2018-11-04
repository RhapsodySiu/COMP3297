from django import forms

SUPPLIES_QUANTITY_CHOICE = [(i, str(i)) for i in range(1, 21)]

class CartAddSupplyForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=SUPPLIES_QUANTITY_CHOICE, coerce=int)
    
    # indicate whether update or add to the existing quantity
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)