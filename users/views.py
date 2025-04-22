import random

from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.cache import cache
from django.core.mail import send_mail
from django.db.utils import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib import messages

from .forms import RegisterForm, ReaderRegisterForm, LibrarianRegisterForm, EmailConfirmationForm
from .models import Speciality, ReaderSpeciality
from .models import Faculty



User = get_user_model()


def register(request):
    """ Вибір типу користувача та email """
    if request.method == "POST":
        print(request.POST)  # Дивись, чи приходить type_user

        form = RegisterForm(request.POST)
        if form.is_valid():
            type_user = form.cleaned_data["type_user"]
            email = form.cleaned_data["email"]

            if type_user == "reader":
                return redirect("register_reader", email=email)

            elif type_user == "librarian":
                confirmation_code = f"{random.randint(100000, 999999)}"
                cache.set(f"email_code_{email}", confirmation_code, timeout=300)

                send_mail(
                    "Код підтвердження реєстрації",
                    f"Ваш код підтвердження: {confirmation_code}",
                    "admin@example.com",
                    [email],
                    fail_silently=False,
                )

                return redirect("confirm_email", uid=urlsafe_base64_encode(force_bytes(email)))

    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})

def confirm_email(request, uid):
    """ Підтвердження email бібліотекаря """
    email = force_str(urlsafe_base64_decode(uid))

    if request.method == "POST":
        form = EmailConfirmationForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data["code"]
            stored_code = cache.get(f"email_code_{email}")

            if stored_code and entered_code == stored_code:
                cache.delete(f"email_code_{email}")  # Видаляємо код після використання
                return redirect("register_librarian", email=email)
            else:
                return HttpResponse("Невірний або прострочений код підтвердження.", status=400)

    else:
        form = EmailConfirmationForm()

    return render(request, "users/confirm_email.html", {"form": form})


def register_librarian(request, email):
    """ Реєстрація бібліотекаря після підтвердження email """
    if User.objects.filter(username=email).exists():
        return HttpResponse("Користувач з таким email вже зареєстрований.", status=400)

    if request.method == "POST":
        form = LibrarianRegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.email = email
                user.username = email
                user.type_user = "librarian"
                user.set_password(form.cleaned_data["password"])
                user.save()
                login(request, user)
                return redirect("home")

            except IntegrityError:
                return HttpResponse("Користувач з таким email вже існує.", status=400)

    else:
        form = LibrarianRegisterForm()
    return render(request, "users/register_librarian.html", {"form": form})

def register_reader(request, email):
    """Реєстрація читача"""
    if User.objects.filter(username=email).exists():
        return HttpResponse("Користувач з таким email вже зареєстрований.", status=400)

    if request.method == "POST":
        form = ReaderRegisterForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    first_name=form.cleaned_data["first_name"],
                    last_name=form.cleaned_data["last_name"],
                    phone=form.cleaned_data["phone"],
                    type_user="reader"
                )
                user.set_password(form.cleaned_data["password"])
                user.save()

                # Автоматично додаємо факультет і спеціальність користувачу
                faculty = form.cleaned_data["faculty"]
                speciality = form.cleaned_data["speciality"]
                ReaderSpeciality.objects.create(user=user, faculty=faculty, speciality=speciality)

                login(request, user)
                return redirect("home")

            except IntegrityError:
                return HttpResponse("Користувач з таким email вже існує.", status=400)

    else:
        form = ReaderRegisterForm()

    return render(request, "users/register_reader.html", {"form": form})


def get_specialities(request):
    """Повертає список спеціальностей для вибраного факультету"""
    faculty_id = request.GET.get("faculty_id")
    specialities = Speciality.objects.filter(faculty_id=faculty_id).values("id", "name")
    return JsonResponse({"specialities": list(specialities)})

@login_required
def home(request):
    """Перегляд профілю користувача"""
    user = request.user
    return render(request, "users/home.html", {"user": user})


def login_view(request):
    """Авторизація користувача"""
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")  # Перенаправлення після успішного логіну
        else:
            # Якщо форма недійсна (наприклад, логін/пароль неправильні)
            messages.error(request, "Невірний логін або пароль.")
    else:
        form = AuthenticationForm()

    return render(request, "users/login.html", {"form": form})

def logout_view(request):
    """Вихід з облікового запису"""
    logout(request)
    return redirect("login")

def get_faculties(request):
    faculties = Faculty.objects.all().values("id", "name")
    data = {"faculties": list(faculties)}
    return JsonResponse(data)

def register_view(request):
    faculties = Faculty.objects.all()  # Отримуємо всі факультети
    print("Факультети передані в шаблон:", faculties)
    return render(request, "users/register_reader.html", {"faculties": faculties})

def index_view(request):
    return render(request, "index.html")





