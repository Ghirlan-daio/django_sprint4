from datetime import datetime, timezone

from blog.models import Category, Post
from django.shortcuts import get_object_or_404, render

LIMIT_POSTS = 5


def index(request):
    """
    Выводит на главную страницу список
    доступных для чтения постов.
    """
    post_list = Post.objects.select_related(
        'category',
        'author',
        'location'
    ).filter(
        pub_date__date__lt=datetime.now(timezone.utc),
        is_published=True,
        category__is_published=True
    )[:LIMIT_POSTS]
    context = {
        'post_list': post_list
    }
    return render(request, 'blog/index.html', context)


def post_detail(request, pk):
    """
    Выводит на отдельную страницу подробную
    информацию об определённом посте.
    """
    post = get_object_or_404(
        Post,
        pub_date__date__lt=datetime.now(timezone.utc),
        is_published=True,
        category__is_published=True,
        pk=pk
    )
    context = {
        'post': post
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """
    Выводит на отдельную страницу информацию
    о всех постах, опубликованных под
    определённой категорией.
    """
    category = get_object_or_404(
        Category,
        is_published=True,
        slug=category_slug
    )
    post_list = category.categories.filter(
        is_published=True,
        pub_date__date__lt=datetime.now(timezone.utc)
    )
    context = {
        'category': category,
        'post_list': post_list
    }
    return render(request, 'blog/category.html', context)
