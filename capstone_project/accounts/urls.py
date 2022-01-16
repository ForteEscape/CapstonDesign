from django.urls import path, re_path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.signin, name='signin'),
    path('logout/', views.logout, name='logout'),
    path('mypage/', views.mypage, name='mypage'),
]