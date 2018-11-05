from django.urls import path
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'order'

urlpatterns = [
    path('', login_required(views.supply_list), name='supply_list'),
    path('search/', views.search_view, name="search_view"),
    path('history/', views.order_history, name="order_history"),
    path('make/', views.order_create, name="order_create"),
    path('dispatch/', views.order_dispatch, name="order_dispatch"),
    url(r'^test/$', views.test_view, name='test_view'),
]