from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('report/', include('Report.urls')),
    path('', views.home_page, name="home_page"),
    path('login/', views.login_page, name="login_page"),
    path('signup/', views.signup_page, name="signup_page"),
    path('logout_page/', views.logout_page, name="logout_page"),


]
