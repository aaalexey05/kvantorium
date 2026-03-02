from django.urls import path
from .views import health, home, contacts

app_name = "core"

urlpatterns = [
    path("", home, name="home"),
    path("health/", health, name="health"),
    path("contacts/", contacts, name="contacts"),
]
