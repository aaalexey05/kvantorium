from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import redirect, render
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
    if request.user.is_authenticated:
        if request.user.role == "admin":
            return redirect("dashboard:admin_home")
        if request.user.role == "teacher":
            return redirect("dashboard:teacher_home")
        return redirect("accounts:profile")

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


def chrome_devtools_manifest(request):
    # Return a valid JSON response to suppress noisy 404 probes from Chrome devtools.
    return JsonResponse(
        {
            "name": "Kvantorium LMS",
            "short_name": "Kvantorium",
            "description": "Local dev endpoint for chrome devtools probe",
        }
    )
