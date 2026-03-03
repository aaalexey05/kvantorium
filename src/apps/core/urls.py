from django.urls import path, re_path
from .views import health, home, contacts, chrome_devtools_manifest

app_name = "core"

urlpatterns = [
    path("", home, name="home"),
    path("health/", health, name="health"),
    path("contacts/", contacts, name="contacts"),
    re_path(
        r"^\.well-known/appspecific/com\.chrome\.devtools\.json$",
        chrome_devtools_manifest,
        name="chrome_devtools_manifest",
    ),
]
