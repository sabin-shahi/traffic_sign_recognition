from django.contrib import admin
from django.urls import path
from .views import checker
from . import views

urlpatterns = [
    path('',views.index, name ='index' ),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('admin/', admin.site.urls),
    path('checker/', checker, name = 'checker'),
    path('user_list/', views.user_list, name = 'user_list'),
]