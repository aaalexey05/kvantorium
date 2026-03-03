from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("courses/", include("apps.courses.urls")),
    path("courses/htmx/", include("apps.courses.urls_htmx")),
    path("news/", include("apps.news.urls")),
    path("achievements/", include("apps.achievements.urls")),
    path("reviews/", include("apps.reviews.urls")),
    path("progress/", include("apps.progress.urls")),
]
