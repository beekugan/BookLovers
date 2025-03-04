from django.contrib import admin
from django.urls import path
from users.views import (register, register_reader, get_specialities, register_librarian,
                         confirm_email, home, login_view, logout_view)

from books.views import add_genre

urlpatterns = [
    path('admin/', admin.site.urls),
    path("add-genre/", add_genre, name="add_genre"),
    path("register/", register, name="register"),
    path("register_reader/<str:email>/", register_reader, name="register_reader"),
    path("register_librarian/<str:email>/", register_librarian, name="register_librarian"),
    path("confirm_email/<str:uid>/", confirm_email, name="confirm_email"),
    path("get_specialities/", get_specialities, name="get_specialities"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    path("home/", home, name="home"),
]
