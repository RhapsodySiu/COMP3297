from django.urls import path
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'warehouse'

urlpatterns = [
    path('', views.order_warehouse, name="order_warehouse"),
    path('processOrder/', views.processOrder, name="processOrder"),
    path('queueForDispatch/', views.queueForDispatch, name="queueForDispatch"),
    path('getShippingLabel/', views.getShippingLabel, name="getShippingLabel")
    # path('detail/<uuid:order_id>/', views.order_detail, name="order_detail")
]
