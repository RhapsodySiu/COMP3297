from django.urls import path
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'dispatch'

urlpatterns = [
    path('', views.order_dispatch, name="order_dispatch"),
    path('downloadItinerary/', views.download_itinerary, name="download_itinerary"),
    path('test/', views.test, name="test")
]