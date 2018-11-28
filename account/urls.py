from django.contrib.auth.views import LoginView, LogoutView
from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^login/$', LoginView.as_view(template_name='account/registration/login.html'), name='login'),
    url(r'^logout/$', LogoutView.as_view(template_name='account/registration/logout.html'), name='logout'),
    path('register/<uuid:tokenFromURL>', views.register, name='register'),
    url(r'^doRegistration/$', views.doRegistration, name='doRegistration'),
    url(r'^generateToken/', views.generateToken, name='token_generation'),
    url(r'^doTokenGeneration/', views.doTokenGeneration, name='doTokenGeneration'),
    url(r'^edit_profile/', views.edit_profile, name="edit_profile")
    #url(r'^logout-then-login/$', logout_then_login, name='logout_then_login'),
]