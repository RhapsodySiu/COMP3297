from django.contrib.auth.views import LoginView, LogoutView
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login/$', LoginView.as_view(template_name='account/registration/login.html'), name='login'),
    url(r'^logout/$', LogoutView.as_view(template_name='account/registration/logout.html'), name='logout'),
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^register/$', views.register, name='register'),
    #url(r'^logout-then-login/$', logout_then_login, name='logout_then_login'),
]