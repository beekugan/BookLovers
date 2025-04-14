from django.core.management import call_command
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.timezone import now, timedelta

from books.models import Book, Publisher, Author, Genre
from logbook.models import ServiceHistory, LineServiceHistory
from notifications.models import Notification
from notifications.utils import notify_user
from users.models import User


class NotificationTests(TestCase):
    def setUp(self):
        self.reader = User.objects.create_user(username='reader', password='readerpass', type_user='reader')
        self.librarian = User.objects.create_user(username='librarian', password='libpass', type_user='librarian')
        self.publisher = Publisher.objects.create(name_publisher="Test Publisher")
        self.author = Author.objects.create(name_author="Test", surname_author="Author")
        self.genre = Genre.objects.create(name_genre="Test Genre")
        self.book = Book.objects.create(
            name="Test Book", publisher=self.publisher, author=self.author,
            genre=self.genre, quantity=1, status='available'
        )
        self.client = Client()

    def test_notify_user_creates_notification(self):
        notify_user(self.reader, "Нагадування про книгу", type="reminder")
        self.assertEqual(Notification.objects.count(), 1)
        n = Notification.objects.first()
        self.assertEqual(n.user, self.reader)
        self.assertEqual(n.type, "reminder")
        self.assertEqual(n.message, "Нагадування про книгу")

    def test_notification_types(self):
        for notif_type in ["reminder", "warning", "block", "unblock"]:
            notify_user(self.reader, f"Повідомлення типу {notif_type}", type=notif_type)
        self.assertEqual(Notification.objects.count(), 4)
        types = Notification.objects.values_list("type", flat=True)
        self.assertIn("block", types)
        self.assertIn("unblock", types)

    def test_user_notifications_view(self):
        notify_user(self.reader, "Тестове повідомлення")
        self.client.login(username='reader', password='readerpass')
        response = self.client.get(reverse('user_notifications'))
        self.assertContains(response, "Тестове повідомлення")
        self.assertTemplateUsed(response, 'notifications/user_notifications.html')

    def test_notification_created_on_overdue(self):
        # Створюємо видачу з простроченою датою повернення
        service = ServiceHistory.objects.create(reader=self.reader, librarian=self.librarian)
        loan = LineServiceHistory.objects.create(
            service_history=service,
            book=self.book,
            date_when_was_taken=now().date() - timedelta(days=10),
            date_when_should_return=now().date() - timedelta(days=1),
        )

        # Імітація логіки check_loans
        from django.core.management import call_command
        call_command('check_loans')

        notifications = Notification.objects.filter(user=self.reader)
        self.assertTrue(any("прострочили" in n.message for n in notifications))
        self.assertIn(notifications.last().type, ["warning", "block"])

    def test_block_notification_and_user_blocked(self):
        # Видача з понад 7 днів прострочення
        service = ServiceHistory.objects.create(reader=self.reader, librarian=self.librarian)
        loan = LineServiceHistory.objects.create(
            service_history=service,
            book=self.book,
            date_when_was_taken=now().date() - timedelta(days=20),
            date_when_should_return=now().date() - timedelta(days=10),
        )

        from django.core.management import call_command
        call_command('check_loans')

        self.reader.refresh_from_db()
        self.assertTrue(self.reader.is_blocked)
        last_notif = Notification.objects.filter(user=self.reader).last()
        self.assertEqual(last_notif.type, 'block')


class NotificationIntegrationTests(TestCase):
    def setUp(self):
        print("\n Створення тестового користувача...")
        self.user = User.objects.create_user(
            username='reader1',
            password='testpass123',
            type_user='reader',
            email='reader1@example.com'
        )
        print(f" Користувача створено: {self.user.username} ({self.user.type_user})")

    def test_notify_user_creates_notification(self):
        print("\n Тест: notify_user створює сповіщення")
        message = "Нагадування про повернення книги"
        notify_user(self.user, message, type='reminder')
        print(" Виклик notify_user завершено")

        notifications = Notification.objects.filter(user=self.user)
        print(f" Знайдено {notifications.count()} сповіщень для користувача {self.user.username}")

        self.assertEqual(notifications.count(), 1)
        notification = notifications.first()

        print(f" Перевірка полів сповіщення...")
        print(f" Повідомлення: {notification.message}")
        print(f" Тип: {notification.type}")
        print(f"️ Прочитано: {notification.is_read}")
        print(f" Дата створення: {notification.created_at}")

        self.assertEqual(notification.message, message)
        self.assertEqual(notification.type, 'reminder')
        self.assertFalse(notification.is_read)
        self.assertLessEqual(notification.created_at.date(), now().date())
        print(" Усі перевірки пройдено успішно!")