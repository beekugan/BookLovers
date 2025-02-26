"""
URL configuration for BookSS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from users.views import register,  register_reader, get_specialities
from books.views import add_genre

urlpatterns = [
    path('admin/', admin.site.urls),
    path("add-genre/", add_genre, name="add_genre"),
    path("register/", register, name="register"),
    path("register_reader/<str:email>/", register_reader, name="register_reader"),

    path("get_specialities/", get_specialities, name="get_specialities"),


]
