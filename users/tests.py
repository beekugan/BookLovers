from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from users.models import Faculty, Speciality, ReaderSpeciality
from users.forms import RegisterForm, ReaderRegisterForm, LibrarianRegisterForm

User = get_user_model()


class UserRegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.faculty = Faculty.objects.create(name="Факультет інформаційних технологій")
        self.speciality = Speciality.objects.create(name="Кібербезпека", faculty=self.faculty)

    def test_register_form_valid_email_and_type(self):
        form_data = {
            "type_user": "reader",
            "email": "student@nubip.edu.ua"
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_register_form_invalid_email_domain(self):
        form_data = {
            "type_user": "reader",
            "email": "test@gmail.com"
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_reader_registration_form_valid(self):
        form_data = {
            "first_name": "Олег",
            "last_name": "Іванов",
            "phone": "0981234567",
            "faculty": self.faculty.id,
            "speciality": self.speciality.id,
            "password": "testpass123"
        }
        form = ReaderRegisterForm(data=form_data)
        form.fields["speciality"].queryset = Speciality.objects.filter(faculty_id=self.faculty.id)
        self.assertTrue(form.is_valid())

    def test_librarian_registration_form_valid(self):
        form_data = {
            "first_name": "Анна",
            "last_name": "Коваль",
            "phone": "0998887766",
            "faculty": self.faculty.id,
            "password": "securepass456"
        }
        form = LibrarianRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_create_reader_user_and_reader_speciality(self):
        response = self.client.post(reverse("register_reader", kwargs={"email": "student@nubip.edu.ua"}), {
            "first_name": "Олег",
            "last_name": "Іванов",
            "phone": "0981234567",
            "faculty": self.faculty.id,
            "speciality": self.speciality.id,
            "password": "testpass123"
        })
        self.assertEqual(response.status_code, 302)  # should redirect to home
        user = User.objects.get(email="student@nubip.edu.ua")
        self.assertEqual(user.first_name, "Олег")
        self.assertEqual(user.type_user, "reader")
        reader_spec = ReaderSpeciality.objects.get(user=user)
        self.assertEqual(reader_spec.speciality, self.speciality)
        self.assertEqual(reader_spec.faculty, self.faculty)

    def test_create_librarian_user_after_email_confirm(self):
        email = "lib@nubip.edu.ua"
        code = "123456"
        cache.set(f"email_code_{email}", code)

        # Використовуємо правильне кодування email як uid
        uid = urlsafe_base64_encode(force_bytes(email))

        # Симуляція підтвердження email
        response = self.client.post(reverse("confirm_email", kwargs={"uid": uid}), {
            "code": code
        })
        self.assertEqual(response.status_code, 302)

        # Симуляція реєстрації бібліотекаря
        response = self.client.post(reverse("register_librarian", kwargs={"email": email}), {
            "first_name": "Анна",
            "last_name": "Коваль",
            "phone": "0998887766",
            "faculty": self.faculty.id,
            "password": "securepass456"
        })
        self.assertEqual(response.status_code, 302)

        user = User.objects.get(email=email)
        self.assertEqual(user.type_user, "librarian")


class ReaderRegistrationIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.faculty = Faculty.objects.create(name="Факультет Інформатики")
        self.speciality = Speciality.objects.create(name="Кібербезпека", faculty=self.faculty)
        self.email = "student@nubip.edu.ua"
        self.password = "SecurePass123"

    def test_reader_registration_creates_user_and_reader_speciality(self):
        url = reverse("register_reader", kwargs={"email": self.email})

        response = self.client.post(url, {
            "first_name": "Іван",
            "last_name": "Іваненко",
            "phone": "+380991112233",
            "faculty": self.faculty.id,
            "speciality": self.speciality.id,
            "password": self.password
        })

        self.assertEqual(response.status_code, 302)  # redirect to "home"

        user = User.objects.get(email=self.email)
        self.assertEqual(user.first_name, "Іван")
        self.assertEqual(user.last_name, "Іваненко")
        self.assertEqual(user.phone, "+380991112233")
        self.assertEqual(user.type_user, "reader")
        self.assertTrue(user.check_password(self.password))

        reader_speciality = ReaderSpeciality.objects.get(user=user)
        self.assertEqual(reader_speciality.faculty, self.faculty)
        self.assertEqual(reader_speciality.speciality, self.speciality)


class LibrarianRegistrationIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.faculty = Faculty.objects.create(name="Факультет Гуманітарних Наук")
        self.email = "librarian@nubip.edu.ua"
        self.password = "StrongPass456"

    def test_librarian_registration_with_email_confirmation(self):
        # Крок 1: Надсилання форми з email і типом користувача
        response = self.client.post(reverse("register"), {
            "type_user": "librarian",
            "email": self.email
        })

        # Має переадресувати на сторінку підтвердження коду
        self.assertEqual(response.status_code, 302)
        uid = urlsafe_base64_encode(force_bytes(self.email))
        self.assertRedirects(response, reverse("confirm_email", kwargs={"uid": uid}))

        # Крок 2: Симулюємо введення правильного коду (встановлюємо його в кеш)
        code = "123456"
        cache.set(f"email_code_{self.email}", code, timeout=300)

        response = self.client.post(reverse("confirm_email", kwargs={"uid": uid}), {
            "code": code
        })

        # Має переадресувати на сторінку реєстрації бібліотекаря
        self.assertRedirects(response, reverse("register_librarian", kwargs={"email": self.email}))

        # Крок 3: Реєстрація бібліотекаря
        response = self.client.post(reverse("register_librarian", kwargs={"email": self.email}), {
            "first_name": "Оксана",
            "last_name": "Савчук",
            "phone": "+380981234567",
            "faculty": self.faculty.id,
            "password": self.password
        })

        # Після реєстрації — редірект на "home"
        self.assertRedirects(response, reverse("home"))

        # Перевіряємо, що користувач створений
        user = User.objects.get(email=self.email)
        self.assertEqual(user.first_name, "Оксана")
        self.assertEqual(user.type_user, "librarian")
        self.assertTrue(user.check_password(self.password))