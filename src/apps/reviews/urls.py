from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path("", views.review_list, name="list"),
    path("submit/", views.review_submit, name="submit"),
]
