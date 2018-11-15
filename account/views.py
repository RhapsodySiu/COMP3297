# For Email Sending
from smtplib import SMTP_SSL, SMTPException
from email.mime.text import MIMEText
from email.utils import formataddr
from enumfields import EnumIntegerField
from enumfields import Enum

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from .forms import LoginForm, RegistrationForm, TokenGenerationForm, RegistrationFormForCM
from .models import Token, Role, ClinicManager
from order.models import Clinic
from django.contrib.auth.decorators import login_required
from django.template.context_processors import csrf

# handle user login
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})

def register(request, tokenFromURL):
    
    if Token.objects.filter(token=tokenFromURL).count() == 0:
        return HttpResponse(status=404)
    
    Email = Token.objects.get(token=tokenFromURL).email
    if str(Token.objects.get(token=tokenFromURL).role) == "Clinic Manager":
        registration_form = RegistrationFormForCM(initial={'token': tokenFromURL, 'email': Email})
    else:
        registration_form = RegistrationForm(initial={'token': tokenFromURL, 'email': Email})
    return render(request, 'account/register.html', {'user_form': registration_form})

def doRegistration(request):
    
    if Token.objects.filter(token=request.POST.get("token")).count() == 0:
        return HttpResponse(status=404)
    
    token = Token.objects.get(token=request.POST.get("token"))
    
    if token.isUsed == True:
        return HttpResponse(status=404)
    
    tokenRole = str(token.role)
    
    if tokenRole == "Clinic Manager":
        registrationForm = RegistrationFormForCM(request.POST)
    else:
        registrationForm = RegistrationForm(request.POST)
        

    
    if registrationForm.is_valid():
        
        # Check if password matches
        if registrationForm.cleaned_data['password'] != registrationForm.cleaned_data['password2']:
            Message = "The password does not match."
            return render(request, 'account/register_error.html', {'message': Message, 'token': registrationForm.cleaned_data['token']})
        
        NewUser = registrationForm.save(commit=False)
        NewUser.set_password(registrationForm.cleaned_data['password'])
        NewUser.save()
        
        # Add the user to the corresponding group
        NewUserGroup = Group.objects.get(name=tokenRole)
        NewUser.groups.set([NewUserGroup])
        
        # If the user is clinic manager, add a mapping between User and Clinic
        if tokenRole == "Clinic Manager":
            ClinicOfCM = Clinic.objects.get(id=registrationForm.cleaned_data['clinic']) 
            NewClinicManager = ClinicManager()
            NewClinicManager.user = NewUser
            NewClinicManager.clinic = ClinicOfCM
            NewClinicManager.save()
        
        # Mark the token as used.
        token.isUsed = True
        token.save()
        return render(request, 'account/register_done.html', {'new_user': NewUser})
    else:
        # In this case, probably the username has been used by others
        Message = "Some information is missing or the username has been used by others."
        return render(request, 'account/register_error.html', {'message': Message, 'token': registrationForm.cleaned_data['token']})
    
    

@login_required
def generateToken(request):
    generate_token_form = TokenGenerationForm()
    return render(request, 'account/generateToken.html', {'TokenGenerationForm': generate_token_form})

@login_required
def doTokenGeneration(request):
    Message = ""
    generationForm = TokenGenerationForm(request.POST)
    if generationForm.is_valid():
        # Check if email exists in Token
        Count = Token.objects.filter(email=generationForm.cleaned_data['email']).count()
        if Count != 0:
            Message = "A token has been generated for this email address."
            return render(request, 'account/generateToken_response.html', {'message': Message})
        # Check if email exists in Users
        Count = User.objects.filter(email=generationForm.cleaned_data['email']).count()
        if Count != 0:
            Message = "This email address has been registered as an user in the system."
            return render(request, 'account/generateToken_response.html', {'message': Message})
        
        # If not exists in Token and Users, record it
        NewToken = Token(email=generationForm.cleaned_data['email'], role=generationForm.cleaned_data['role'])
        NewToken.save();
        
        # Send email
        mailHost = "smtp.zoho.com"
        mailUsername = "admin@accoladehk.com"
        mailPassword = "knb9A1Zv3b3U"
        sender = "admin@accoladehk.com"
        receiver = [generationForm.cleaned_data['email']]
        
        mailMessage = "Hi, <br><br> Please register for the AS-P system with the <a href=\"http://127.0.0.1:8000/register/" + str(NewToken.token) + "\">link here</a>. <br><br> Regards,<br>Hospital Authority"
        message = MIMEText(mailMessage, 'html', 'utf-8')
        message['Subject'] = "Registration Token on AS-P"
        message['From'] = formataddr(["Hospital Authority",sender])
        
        try:
            smtpObj = SMTP_SSL(mailHost, 465) 
            smtpObj.login(mailUsername, mailPassword)  
            smtpObj.sendmail(sender, receiver, message.as_string())
            print("Email Sent")
        except SMTPException:
            print("Failed to send email")
            
        Message = "Successful."
    else:
        Message = "Error."
    return render(request, 'account/generateToken_response.html', {'message': Message})

# the dashboard
@login_required
def dashboard(request):
    #set section to track where the user is watching
    return render(request, 'account/dashboard.html', {'section': 'dashboard'})