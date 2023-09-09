from datetime import datetime, timezone

from blog.models import Post
from django.core.paginator import Paginator
from django.db.models import Count


def paginate_page(request, object_list, objects_on_page):
    """Пагинатор."""
    paginator = Paginator(object_list, objects_on_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def queryset_filter(query):
    """
    Фильтрация запросов к моделям
    приложения "blog".
    """
    return query.filter(
        pub_date__date__lt=datetime.now(timezone.utc),
        is_published=True,
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


def query_select_related():
    """
    Запрос к связанным моделям приложения "blog"
    с фильтрацией по статусу категории.
    """
    return Post.objects.select_related(
        'category', 'location', 'author'
    ).filter(category__is_published=True)
