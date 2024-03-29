from django.urls import path
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'order'

urlpatterns = [
    path('', login_required(views.supply_list), name='supply_list'),
    path('search/<int:category>/', views.category_view, name='category_view'),
    path('search/', views.search_view, name="search_view"),
    path('history/', views.order_history, name="order_history"),
    path('make/', views.order_create, name="order_create"),
    path('detail/<str:order_id>/', views.order_detail, name="order_detail"),
    path('cancel/<str:order_id>/', views.cancel_order, name="cancel_order"),
    path('delivered/<str:order_id>/', views.mark_delivered, name="mark_delivered"),
    url(r'^test/$', views.test_view, name='test_view'),
]
