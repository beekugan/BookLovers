from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from books.models import Book, Author, Genre, Publisher


class BookViewsTestCase(TestCase):
    def setUp(self):
        # Створюємо користувача-бібліотекаря і логінимось
        self.client = Client()
        self.librarian = User.objects.create_user(
            username='lib1', password='pass1234', type_user='librarian')
        self.client.login(username='lib1', password='pass1234')

        # Додаткові об'єкти
        self.publisher = Publisher.objects.create(name_publisher='Test Publisher')
        self.author = Author.objects.create(name_author='John', surname_author='Doe')
        self.genre = Genre.objects.create(name_genre='Drama')

    def test_create_book(self):
        response = self.client.post(reverse('book_add'), {
            'name': 'New Book',
            'publisher': self.publisher.id,
            'author': self.author.id,
            'genre': self.genre.id,
            'quantity': 5,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Book.objects.filter(name='New Book').exists())

    def test_update_book_get(self):
        book = Book.objects.create(
            name='Book to Edit',
            publisher=self.publisher,
            author=self.author,
            genre=self.genre,
            quantity=3
        )
        response = self.client.get(reverse('book_edit_detail', args=[book.id]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'id': book.id,
                'name': 'Book to Edit',
                'publisher': self.publisher.id,
                'author': self.author.id,
                'genre': self.genre.id,
                'quantity': 3
            }
        )

    def test_update_book_post(self):
        book = Book.objects.create(
            name='Old Name',
            publisher=self.publisher,
            author=self.author,
            genre=self.genre,
            quantity=1
        )
        response = self.client.post(reverse('book_edit_detail', args=[book.id]), {
            'name': 'Updated Name',
            'publisher': self.publisher.id,
            'author': self.author.id,
            'genre': self.genre.id,
            'quantity': 2,
        })
        self.assertEqual(response.status_code, 302)
        book.refresh_from_db()
        self.assertEqual(book.name, 'Updated Name')

    def test_delete_book(self):
        book = Book.objects.create(
            name='Delete Me',
            publisher=self.publisher,
            author=self.author,
            genre=self.genre,
            quantity=1
        )
        response = self.client.post(reverse('book_delete', args=[book.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Book.objects.filter(id=book.id).exists())

    def test_create_author(self):
        response = self.client.post(reverse('author_add'), {
            'name_author': 'Jane',
            'surname_author': 'Smith'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Author.objects.filter(name_author='Jane').exists())

    def test_update_author_post(self):
        author = Author.objects.create(name_author='Mark', surname_author='Twain')
        response = self.client.post(reverse('author_edit_detail', args=[author.id]), {
            'name_author': 'Samuel',
            'surname_author': 'Clemens'
        })
        self.assertEqual(response.status_code, 302)
        author.refresh_from_db()
        self.assertEqual(author.name_author, 'Samuel')

    def test_delete_author(self):
        author = Author.objects.create(name_author='Delete', surname_author='Author')
        response = self.client.post(reverse('author_delete', args=[author.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Author.objects.filter(id=author.id).exists())

    def test_create_genre(self):
        response = self.client.post(reverse('genre_add'), {
            'name_genre': 'Sci-Fi'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Genre.objects.filter(name_genre='Sci-Fi').exists())

    def test_create_publisher(self):
        response = self.client.post(reverse('publisher_add'), {
            'name_publisher': 'New Publisher'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Publisher.objects.filter(name_publisher='New Publisher').exists())

class BooksIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.librarian = User.objects.create_user(
            username='librarian_user',
            password='testpassword',
            type_user='librarian'
        )
        self.client.login(username='librarian_user', password='testpassword')

        self.publisher = Publisher.objects.create(name_publisher='Видавництво Книжка')
        self.author = Author.objects.create(name_author='Іван', surname_author='Франко')
        self.genre = Genre.objects.create(name_genre='Фентезі')

    def test_create_book(self):
        response = self.client.post(reverse('book_add'), {
            'name': 'Лісова пісня',
            'publisher': self.publisher.id,
            'author': self.author.id,
            'genre': self.genre.id,
            'quantity': 3
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Book.objects.filter(name='Лісова пісня').exists())

    def test_update_book(self):
        book = Book.objects.create(
            name='Стара назва',
            publisher=self.publisher,
            author=self.author,
            genre=self.genre,
            quantity=2
        )
        response = self.client.post(reverse('book_edit_detail', args=[book.id]), {
            'name': 'Нова назва',
            'publisher': self.publisher.id,
            'author': self.author.id,
            'genre': self.genre.id,
            'quantity': 5
        })
        self.assertEqual(response.status_code, 302)
        book.refresh_from_db()
        self.assertEqual(book.name, 'Нова назва')
        self.assertEqual(book.quantity, 5)

    def test_delete_book(self):
        book = Book.objects.create(
            name='На видалення',
            publisher=self.publisher,
            author=self.author,
            genre=self.genre,
            quantity=1
        )
        response = self.client.post(reverse('book_delete', args=[book.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Book.objects.filter(id=book.id).exists())

    def test_create_author(self):
        response = self.client.post(reverse('author_add'), {
            'name_author': 'Леся',
            'surname_author': 'Українка'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Author.objects.filter(name_author='Леся', surname_author='Українка').exists())

    def test_create_genre(self):
        response = self.client.post(reverse('genre_add'), {
            'name_genre': 'Драма'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Genre.objects.filter(name_genre='Драма').exists())

    def test_create_publisher(self):
        response = self.client.post(reverse('publisher_add'), {
            'name_publisher': 'Видавництво Соняшник'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Publisher.objects.filter(name_publisher='Видавництво Соняшник').exists())