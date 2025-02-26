from django.contrib.auth import get_user_model, login
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import RegisterForm, ReaderRegisterForm, LibrarianRegisterForm
from .models import Speciality, ReaderSpeciality
from .models import User

User = get_user_model()

def register(request):
    """ Вибір типу користувача та email """
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            type_user = form.cleaned_data["type_user"]
            email = form.cleaned_data["email"]

            if type_user == "reader":
                return redirect("register_reader", email=email)

            elif type_user == "librarian":
                # Генерація токена
                uid = urlsafe_base64_encode(force_bytes(email))
                token_url = f"http://{get_current_site(request)}{reverse('confirm_email', args=[uid])}"

                # Відправка email
                send_mail(
                    "Підтвердження реєстрації",
                    f"Перейдіть за посиланням для продовження реєстрації: {token_url}",
                    "admin@example.com",
                    [email],
                    fail_silently=False,
                )
                return HttpResponse("На вашу пошту надіслано лист для підтвердження реєстрації.")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})

def confirm_email(request, uid):
    """ Підтвердження email бібліотекаря """
    email = force_str(urlsafe_base64_decode(uid))
    return redirect("register_librarian", email=email)



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


def get_specialities(request):
    """Повертає список спеціальностей для вибраного факультету"""
    faculty_id = request.GET.get("faculty_id")
    specialities = Speciality.objects.filter(faculty_id=faculty_id).values("id", "name")
    return JsonResponse({"specialities": list(specialities)})

