from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from gestion_usuarios import views

urlpatterns = [
    path('', views.index, name='index'),  
    path('usuarios/', include('gestion_usuarios.urls')),
    path('admin/', admin.site.urls),
]
