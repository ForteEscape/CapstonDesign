from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.signin, name='signin'),
    path('logout/', views.logout, name='logout'),
    path('mypage/', views.mypage, name='mypage'),
    path('pwd_change/', views.pwd_change, name='pwd_change'),
    path('membership_withdraw/', views.membership_withdraw, name='withdraw'),
]

