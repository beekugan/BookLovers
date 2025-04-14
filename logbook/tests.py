from datetime import timedelta

from django.test import TestCase, Client
from django.urls import reverse
from django.utils.timezone import now
from users.models import User, Faculty, Speciality, ReaderSpeciality
from books.models import Book, Author, Genre, Publisher
from logbook.models import ServiceHistory, LineServiceHistory, BookRequest



class LogbookTests(TestCase):
    def setUp(self):
        # Користувачі
        self.reader = User.objects.create_user(username='reader1', password='testpass', type_user='reader')
        self.librarian = User.objects.create_user(username='librarian1', password='testpass', type_user='librarian')

        # Дані для книг
        self.publisher = Publisher.objects.create(name_publisher="Видавництво Тест")
        self.author = Author.objects.create(name_author="Іван", surname_author="Іваненко")
        self.genre = Genre.objects.create(name_genre="Фентезі")
        self.book = Book.objects.create(
            name="Тестова книга",
            publisher=self.publisher,
            author=self.author,
            genre=self.genre,
            quantity=3,
            status='available'
        )

    def test_service_history_creation(self):
        """Тест створення журналу видачі (ServiceHistory)"""
        history = ServiceHistory.objects.create(reader=self.reader, librarian=self.librarian)
        self.assertEqual(len(history.loan_code), 4)
        self.assertEqual(history.reader, self.reader)
        self.assertTrue(history.loan_code.isupper())

    def test_line_service_history_sets_returned_status(self):
        """Тест, що статус книги оновлюється при поверненні"""
        history = ServiceHistory.objects.create(reader=self.reader, librarian=self.librarian)
        line = LineServiceHistory.objects.create(
            service_history=history,
            book=self.book,
            date_when_returned=now().date()
        )
        line.refresh_from_db()
        self.book.refresh_from_db()
        self.assertEqual(line.status, 'returned')
        self.assertEqual(self.book.status, 'available')

    def test_book_request_creation(self):
        """Тест створення запиту на книгу"""
        request = BookRequest.objects.create(reader=self.reader, book=self.book)
        self.assertEqual(len(request.request_code), 6)
        self.assertFalse(request.is_approved)
        self.assertEqual(request.book, self.book)

    def test_approve_book_request_changes_status(self):
        """Тест, що при підтвердженні запиту створюється історія і зменшується кількість книг"""
        request = BookRequest.objects.create(reader=self.reader, book=self.book)
        request.is_approved = True
        request.save()
        history = ServiceHistory.objects.create(reader=self.reader, librarian=self.librarian)
        LineServiceHistory.objects.create(service_history=history, book=self.book)
        self.book.quantity -= 1
        if self.book.quantity == 0:
            self.book.status = 'borrowed'
        self.book.save()
        self.book.refresh_from_db()
        self.assertLessEqual(self.book.quantity, 2)

    def test_line_service_history_due_date_default(self):
        """Тест, що дата повернення за замовчуванням — через 14 днів"""
        history = ServiceHistory.objects.create(reader=self.reader, librarian=self.librarian)
        line = LineServiceHistory.objects.create(service_history=history, book=self.book)
        expected_return_date = now().date() + now().utcnow().astimezone().utcoffset() + timedelta(days=14)
        self.assertEqual(line.date_when_should_return, expected_return_date)


class LogbookIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Створення користувачів
        self.librarian = User.objects.create_user(username='librarian', password='testpass', type_user='librarian')
        self.reader = User.objects.create_user(username='reader', password='testpass', type_user='reader')

        # Створення пов’язаних моделей
        self.publisher = Publisher.objects.create(name_publisher='Test Publisher')
        self.author = Author.objects.create(name_author='John', surname_author='Doe')
        self.genre = Genre.objects.create(name_genre='Fiction')

        # Створення книги
        self.book = Book.objects.create(
            name='Test Book',
            publisher=self.publisher,
            author=self.author,
            genre=self.genre,
            quantity=2,
            status='available'
        )

    def test_issue_and_return_book(self):
        self.client.login(username='librarian', password='testpass')

        # Видача книги
        response = self.client.post(reverse('issue_book'), {
            'reader': self.reader.id,
            'book': self.book.id,
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ServiceHistory.objects.count(), 1)
        self.assertEqual(LineServiceHistory.objects.count(), 1)

        self.book.refresh_from_db()
        self.assertEqual(self.book.quantity, 1)
        self.assertEqual(self.book.status, 'borrowed')

        loan_code = ServiceHistory.objects.first().loan_code

        # Блокуємо читача вручну
        self.reader.is_blocked = True
        self.reader.save()

        # Повернення книги
        response = self.client.post(reverse('return_book'), {
            'loan_code': loan_code,
        }, follow=True)

        self.assertEqual(response.status_code, 200)

        self.book.refresh_from_db()
        self.assertEqual(self.book.quantity, 2)
        self.assertEqual(self.book.status, 'available')

        # Читач має бути розблокований
        self.reader.refresh_from_db()
        self.assertFalse(self.reader.is_blocked)

    def test_create_and_approve_book_request(self):
        self.client.login(username='reader', password='testpass')

        # Створення запиту
        response = self.client.post(reverse('create_book_request'), {
            'book': self.book.id
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(BookRequest.objects.count(), 1)

        book_request = BookRequest.objects.first()
        self.assertFalse(book_request.is_approved)

        self.client.logout()
        self.client.login(username='librarian', password='testpass')

        # Підтвердження запиту
        response = self.client.get(
            reverse('approve_book_request', args=[book_request.request_code]), follow=True)
        self.assertEqual(response.status_code, 200)

        book_request.refresh_from_db()
        self.assertTrue(book_request.is_approved)

        self.assertEqual(ServiceHistory.objects.count(), 1)
        self.assertEqual(LineServiceHistory.objects.count(), 1)

        self.book.refresh_from_db()
        self.assertEqual(self.book.quantity, 1)


    def test_reader_history_view(self):
        self.client.login(username='librarian', password='testpass')

        # Створення запису про видачу
        history = ServiceHistory.objects.create(reader=self.reader, librarian=self.librarian)
        LineServiceHistory.objects.create(
            service_history=history,
            book=self.book,
            date_when_was_taken=now().date(),
            date_when_should_return=now().date() + timedelta(days=14),
        )
        self.client.logout()

        # Перевірка історії користувача
        self.client.login(username='reader', password='testpass')
        response = self.client.get(reverse('user_history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book.name)