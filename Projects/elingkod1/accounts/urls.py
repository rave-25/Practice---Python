from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard),
    path('client/', views.client),
    path('orders/', views.orders),
    path('issues/', views.issues),
]
