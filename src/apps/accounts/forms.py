from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({"placeholder": "you@example.com"})
        self.fields["first_name"].widget.attrs.update({"placeholder": "Имя"})
        self.fields["last_name"].widget.attrs.update({"placeholder": "Фамилия"})
        self.fields["password1"].widget.attrs.update({"placeholder": "Минимум 8 символов"})
        self.fields["password2"].widget.attrs.update({"placeholder": "Повторите пароль"})
        self.fields["role"].choices = [
            (User.Role.STUDENT, "Ученик"),
            (User.Role.PARENT, "Родитель"),
            (User.Role.TEACHER, "Преподаватель"),
        ]

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "first_name", "last_name", "role")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "role", "is_active", "is_staff")


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com", "autofocus": True}),
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Введите пароль"}),
    )
