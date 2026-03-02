from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render
from apps.courses.models import Course
from apps.news.models import NewsPost
from apps.achievements.models import Achievement
from apps.reviews.forms import ReviewForm
from apps.reviews.models import Review
from .models import ContactInfo


def health(request):
    return JsonResponse({
        "status": "ok",
        "time": timezone.now(),
    })


def home(request):
    courses = Course.objects.filter(status="published")[:3]
    news = NewsPost.objects.filter(status="published")[:3]
    achievements = Achievement.objects.all()[:3]
    review_form = ReviewForm()
    reviews = Review.objects.filter(is_approved=True)[:4]
    return render(
        request,
        "core/home.html",
        {"courses": courses, "news": news, "achievements": achievements, "review_form": review_form, "reviews": reviews},
    )


def contacts(request):
    info = ContactInfo.objects.first()
    return render(request, "core/contacts.html", {"info": info})
