from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
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
    url(r'^edit_profile/', views.edit_profile, name="edit_profile"),
    url(r'^changePassword/$', views.change_password, name='change_password'),
	url(r'^password_reset/$', PasswordResetView.as_view(), name='passwordReset'),
    url(r'^password_reset/done/$', PasswordResetDoneView.as_view(), name='password_reset_done'),
	url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^reset/done/$', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    #url(r'^logout-then-login/$', logout_then_login, name='logout_then_login'),
]