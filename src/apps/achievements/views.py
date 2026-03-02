from django.shortcuts import render
from .models import Achievement


def achievements_list(request):
    items = Achievement.objects.all()
    return render(request, "achievements/achievements_list.html", {"items": items})
