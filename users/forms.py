from django import forms

from .models import Faculty, User, Speciality


class RegisterForm(forms.Form):
    """Форма вибору типу користувача та email"""
    TYPE_CHOICES = [
        ('reader', 'Читач'),
        ('librarian', 'Бібліотекар'),
    ]
    type_user = forms.ChoiceField(label="Тип користувача", choices=TYPE_CHOICES, required=True)
    email = forms.EmailField(label="Електронна пошта", required=True)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email.endswith("@nubip.edu.ua"):
            raise forms.ValidationError("Використовуйте email у домені @nubip.edu.ua")
        return email

class ReaderRegisterForm(forms.Form):
    first_name = forms.CharField(label="Ім'я", max_length=100)
    last_name = forms.CharField(label="Прізвище", max_length=100)
    phone = forms.CharField(label="Телефон", max_length=20)
    faculty = forms.ModelChoiceField(label="Факультет", queryset=Faculty.objects.all(), required=True)
    speciality = forms.ModelChoiceField(label="Спеціальність", queryset=Speciality.objects.none(), required=True)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "faculty" in self.data:
            try:
                faculty_id = int(self.data.get("faculty"))
                self.fields["speciality"].queryset = Speciality.objects.filter(faculty_id=faculty_id)
            except (ValueError, TypeError):
                pass



class LibrarianRegisterForm(forms.ModelForm):
    """Форма реєстрації бібліотекаря після підтвердження email"""
    first_name = forms.CharField(label="Ім'я", max_length=100)
    last_name = forms.CharField(label="Прізвище", max_length=100)
    phone = forms.CharField(label="Телефон", max_length=20)
    faculty = forms.ModelChoiceField(label="Факультет", queryset=Faculty.objects.all(), required=True)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "faculty", "password"]

    def save(self, commit=True, email=None):
        user = super().save(commit=False)
        user.email = email
        user.username = email
        user.type_user = "librarian"
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class EmailConfirmationForm(forms.Form):
    """Форма підтвердження email через код"""
    code = forms.CharField(label="Код підтвердження", max_length=6)
