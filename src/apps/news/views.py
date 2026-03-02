from django.shortcuts import get_object_or_404, render
from .models import NewsPost


def news_list(request):
    posts = NewsPost.objects.filter(status="published")
    return render(request, "news/news_list.html", {"posts": posts})


def news_detail(request, slug):
    post = get_object_or_404(NewsPost, slug=slug, status="published")
    return render(request, "news/news_detail.html", {"post": post})
