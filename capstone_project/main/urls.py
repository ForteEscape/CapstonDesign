from django.urls import path, include
from . import views

index_patterns = [
    path('', views.index),
    path('index/', views.index, name='index'),
    path('stockanalysis/', views.stockanalysis, name='stock'),
]

urlpatterns = [
    path('', include(index_patterns))
]