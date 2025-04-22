from django.contrib import admin
from django.urls import path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from books import api_views
from users.api_views import (
    UserListAPIView, UserDetailAPIView,
    FacultyListAPIView, SpecialityListAPIView,
    ReaderSpecialityListAPIView
)
from logbook.api_views import (
    ServiceHistoryListCreateAPIView, ServiceHistoryDetailAPIView,
    LineServiceHistoryListCreateAPIView, LineServiceHistoryDetailAPIView,
    BookRequestListCreateAPIView, BookRequestDetailAPIView
)
from notifications.api_views import (
    NotificationListAPIView,
    NotificationDetailAPIView,
)
from reports.api_views import LoanReportAPIView, BookReportAPIView
from books.views import (
    tools, book_create, book_update, book_delete, book_detail, author_create,
    author_update, author_delete, genre_create, genre_update, genre_delete,
    publisher_create, publisher_update, publisher_delete

)
from logbook.views import (issue_book, return_book, user_history,
                           create_book_request, pending_book_requests, approve_book_request, user_book_requests)
from notifications.views import user_notifications
from reports.views import report_view
from users.views import (
    register, register_reader, get_specialities, register_librarian,
    confirm_email, home, login_view, logout_view, get_faculties, index_view,
)

schema_view = get_schema_view(
   openapi.Info(
      title="Library API",
      default_version='v1',
      description="Документація для API бібліотеки",
      contact=openapi.Contact(email="kn22-t.bezushko@nubip.edu.ua"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index_view, name="index"),

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

    # Видача/повернення
    path('issue/', issue_book, name='issue_book'),
    path('return/', return_book, name='return_book'),

    # Перегляд історії видач (Користувач)
    path("history/", user_history, name="user_history"),

    # Користувач створює запит на отримання книги
    path('request-book/', create_book_request, name='create_book_request'),

    # Бібліотекар переглядає запити, що очікують підтвердження
    path('pending-requests/', pending_book_requests, name='pending_book_requests'),

    # Бібліотекар підтверджує запит на видачу книги
    path('approve-request/<str:request_code>/', approve_book_request, name='approve_book_request'),

    path('my-requests/', user_book_requests, name='user_book_requests'),

    # Сповіщення
    path('notifications/', user_notifications, name='user_notifications'),

    # Звіти
    path('reports/', report_view, name='report_view'),

    # API-документація
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('books/', api_views.BookListCreateAPIView.as_view(), name='book-list-create'),
    path('books/<int:pk>/', api_views.BookRetrieveUpdateDestroyAPIView.as_view(), name='book-detail'),

    path('users/users/', UserListAPIView.as_view(), name='api_users'),
    path('users/users/<int:pk>/', UserDetailAPIView.as_view(), name='api_user_detail'),
    path('users/faculties/', FacultyListAPIView.as_view(), name='api_faculties'),
    path('users/specialities/', SpecialityListAPIView.as_view(), name='api_specialities'),
    path('users/reader-specialities/', ReaderSpecialityListAPIView.as_view(), name='api_reader_specialities'),

    path('logbook/service-history/', ServiceHistoryListCreateAPIView.as_view(), name='api_service_history'),
    path('logbook/service-history/<int:pk>/', ServiceHistoryDetailAPIView.as_view(), name='api_service_history_detail'),

    # LineServiceHistory
    path('logbook/line-service-history/', LineServiceHistoryListCreateAPIView.as_view(), name='api_line_service_history'),
    path('logbook/line-service-history/<int:pk>/', LineServiceHistoryDetailAPIView.as_view(), name='api_line_service_history_detail'),

    # BookRequest
    path('logbook/book-requests/', BookRequestListCreateAPIView.as_view(), name='api_book_requests'),
    path('logbook/book-requests/<int:pk>/', BookRequestDetailAPIView.as_view(), name='api_book_request_detail'),

    path('notifications/api/', NotificationListAPIView.as_view(), name='api_notifications'),
    path('notifications/api/<int:pk>/', NotificationDetailAPIView.as_view(), name='api_notification_detail'),

    path('reports/api/loans/', LoanReportAPIView.as_view(), name='api_report_loans'),
    path('reports/api/books/', BookReportAPIView.as_view(), name='api_report_books')
]



