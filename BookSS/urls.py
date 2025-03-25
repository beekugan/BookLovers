from django.contrib import admin
from django.urls import path
from users.views import (
    register, register_reader, get_specialities, register_librarian,
    confirm_email, home, login_view, logout_view, get_faculties
)
from books.views import (
    tools, book_create, book_update, book_delete, book_detail, author_create,
    author_update, author_delete, genre_create, genre_update, genre_delete,
    publisher_create, publisher_update, publisher_delete

)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Реєстрація та авторизація
    path("register/", register, name="register"),
    path("register_reader/<str:email>/", register_reader, name="register_reader"),
    path("register_librarian/<str:email>/", register_librarian, name="register_librarian"),
    path("confirm_email/<str:uid>/", confirm_email, name="confirm_email"),
    path("get_specialities/", get_specialities, name="get_specialities"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # Головна сторінка
    path("home/", home, name="home"),
    path("get_faculties/", get_faculties, name="get_faculties"),

    # Інструменти бібліотекаря
    path('tools/', tools, name='tools'),

    # 🔹 Книги
    path('books/add/', book_create, name='book_add'),
    path('books/edit/', book_update, name='book_edit'),
    path('books/edit/<int:pk>/', book_update, name='book_edit_detail'),  # Детальне редагування
    path('books/delete/<int:pk>/', book_delete, name='book_delete'),
    path('books/detail/<int:book_id>/', book_detail, name='book_detail'),

    # 🔹 Автори
    path('authors/add/', author_create, name='author_add'),
    path('authors/edit/', author_update, name='author_edit'),  # Сторінка вибору автора для редагування
    path('authors/edit/<int:pk>/', author_update, name='author_edit_detail'),  # Детальне редагування
    path('authors/delete/<int:pk>/', author_delete, name='author_delete'),

    # 🔹 Жанри
    path('genres/add/', genre_create, name='genre_add'),
    path('genres/edit/', genre_update, name='genre_edit'),  # Сторінка вибору жанру для редагування
    path('genres/edit/<int:pk>/', genre_update, name='genre_edit_detail'),  # Детальне редагування
    path('genres/delete/<int:pk>/', genre_delete, name='genre_delete'),

    # 🔹 Видавництва
    path('publishers/add/', publisher_create, name='publisher_add'),
    path('publishers/edit/', publisher_update, name='publisher_edit'),  # Сторінка вибору видавництва для редагування
    path('publishers/edit/<int:pk>/', publisher_update, name='publisher_edit_detail'),  # Детальне редагування
    path('publishers/delete/<int:pk>/', publisher_delete, name='publisher_delete'),
]
