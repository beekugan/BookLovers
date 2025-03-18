from django.contrib import admin
from django.urls import path
from users.views import (register, register_reader, get_specialities, register_librarian,
                         confirm_email, home, login_view, logout_view, get_faculties)
from books.views import (tools, book_create, book_update, book_delete, author_create,
                        author_update, author_delete, genre_create, genre_update, genre_delete,
                        publisher_create, publisher_update, publisher_delete)




urlpatterns = [
    path('admin/', admin.site.urls),

    path("register/", register, name="register"),
    path("register_reader/<str:email>/", register_reader, name="register_reader"),
    path("register_librarian/<str:email>/", register_librarian, name="register_librarian"),
    path("confirm_email/<str:uid>/", confirm_email, name="confirm_email"),
    path("get_specialities/", get_specialities, name="get_specialities"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    path("home/", home, name="home"),
    path("get_faculties/", get_faculties, name="get_faculties"),

    path('tools/', tools, name='tools'),

    # Маршрути для книг
    path('books/add/', book_create, name='book_add'),
    path('books/edit/<int:pk>/', book_update, name='book_edit'),
    path('books/delete/<int:pk>/', book_delete, name='book_delete'),

    # Маршрути для авторів
    path('authors/add/', author_create, name='author_add'),
    path('authors/edit/<int:pk>/', author_update, name='author_edit'),
    path('authors/delete/<int:pk>/', author_delete, name='author_delete'),

    # Маршрути для жанрів
    path('genres/add/', genre_create, name='genre_add'),
    path('genres/edit/<int:pk>/', genre_update, name='genre_edit'),
    path('genres/delete/<int:pk>/', genre_delete, name='genre_delete'),

    # Маршрути для видавництв
    path('publishers/add/', publisher_create, name='publisher_add'),
    path('publishers/edit/<int:pk>/', publisher_update, name='publisher_edit'),
    path('publishers/delete/<int:pk>/', publisher_delete, name='publisher_delete'),


]
