from django.urls import path, include
from . import views

index_patterns = [
    path('', views.index),
    path('index/', views.index, name='index'),
    path('stockanalysis/', views.stockanalysis, name='stock'),
    path('stockanalysis/accounts/logout', views.logout, name='logout')
]

urlpatterns = [
    path('', include(index_patterns))
]