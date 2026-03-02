from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Review
from .forms import ReviewForm


def review_list(request):
    reviews = Review.objects.filter(is_approved=True)
    return render(request, "reviews/review_list.html", {"reviews": reviews, "form": ReviewForm()})


def review_submit(request):
    if request.method != "POST":
        return redirect("reviews:list")
    form = ReviewForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "Спасибо! Отзыв отправлен на модерацию.")
    else:
        messages.error(request, "Исправьте ошибки формы.")
    return redirect(request.META.get("HTTP_REFERER", "reviews:list"))
