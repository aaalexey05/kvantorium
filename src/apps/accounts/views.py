from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from apps.courses.models import Enrollment
from apps.progress.models import CourseProgress


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("core:home")
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    enrollments = list(
        Enrollment.objects.filter(user=request.user)
        .select_related("course")
        .order_by("-created_at")
    )
    progress_records = CourseProgress.objects.filter(user=request.user).select_related("course")
    progress_map = {record.course_id: record for record in progress_records}
    enrollment_cards = []
    for enrollment in enrollments:
        progress_record = progress_map.get(enrollment.course_id)
        enrollment_cards.append(
            {
                "enrollment": enrollment,
                "progress_percent": progress_record.percent if progress_record else 0,
            }
        )
    created_courses = request.user.courses.all().order_by("-created_at")[:5]
    return render(
        request,
        "accounts/profile.html",
        {
            "enrollment_cards": enrollment_cards,
            "created_courses": created_courses,
        },
    )
