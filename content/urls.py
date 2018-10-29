from django.urls import path
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    url(r'^$', login_required(views.ShowSuppliesView.as_view()), name='supplies_view'),
    url(r'^test/$', views.test_view, name='test_view'),
]