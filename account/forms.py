from django import forms
from django.contrib.auth.models import User
from enumfields import EnumField
from .models import ClinicManager, Token, Role
from order.models import Clinic

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    
class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget = forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget = forms.PasswordInput)
    token = forms.UUIDField(widget = forms.HiddenInput())
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

class RegistrationFormForCM(RegistrationForm):
    clinic_choices = []
    for clinic in Clinic.objects.all():
        clinic_choices.append([clinic.id, clinic.name])
    clinic = forms.ChoiceField(choices=clinic_choices)
    class Meta(RegistrationForm.Meta):
        fields = RegistrationForm.Meta.fields + ('clinic',)

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class TokenGenerationForm(forms.ModelForm):
    role = EnumField(Role).formfield()
    class Meta:
        model = Token
        fields = ('email', 'role')
        
'''class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('clinic')'''