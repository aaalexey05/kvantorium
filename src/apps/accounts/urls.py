from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import CustomAuthenticationForm
from .views import register, profile

app_name = "accounts"

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html", authentication_form=CustomAuthenticationForm),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="core:home"), name="logout"),
    path("register/", register, name="register"),
    path("profile/", profile, name="profile"),
]
