from datetime import datetime, timezone

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from utils import paginate_page, query_select_related, queryset_filter

from .constants import POSTS_ON_THE_PAGE
from .forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post, User


class PostListView(ListView):
    """
    Список публикаций пользователей
    на главной странице.
    """
    queryset = queryset_filter(query_select_related())
    paginate_by = POSTS_ON_THE_PAGE
    template_name = 'blog/index.html'


class PostDetailView(DetailView):
    """
    Cтраница отдельной публикации.
    """
    model = Post
    paginate_by = POSTS_ON_THE_PAGE
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        if (
            self.object.author != self.request.user
            and (
                not self.object.is_published
                or not self.object.category.is_published
                or self.object.pub_date > datetime.now(timezone.utc)
            )
        ):
            raise Http404('Публикация не существует.')
        return context


def category_posts(request: HttpRequest, category_slug: str) -> HttpResponse:
    """
    Страница публикаций по
    выбранной категории.
    """
    category = get_object_or_404(
        Category,
        is_published=True,
        slug=category_slug
    )
    post_list = queryset_filter(
        category.posts_category
    )
    context = {
        'category': category,
        'post_list': post_list,
        'page_obj': paginate_page(request, post_list, POSTS_ON_THE_PAGE)
    }
    return render(request, 'blog/category.html', context)


class ProfileListView(ListView):
    """
    Страница профиля пользователя.
    """
    template_name = 'blog/profile.html'
    paginate_by = POSTS_ON_THE_PAGE

    def get_queryset(self):
        self.user = get_object_or_404(
            User, username=self.kwargs['username']
        )
        if self.user == self.request.user:
            return (
                Post.objects.select_related(
                    'category', 'location', 'author'
                ).filter(author=self.user).annotate(
                    comment_count=Count('comments')
                ).order_by('-pub_date')
            )
        return queryset_filter(query_select_related())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.user
        context['user'] = self.user
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    Страница редактирования
    профиля пользователя.
    """
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user}
        )


class PostMixin:
    """
    Миксин для страниц добавления
    и редактирования публикаций.
    """
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    """
    Добавление публикации.
    """
    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user}
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, PostMixin, UpdateView):
    """
    Редактирование публикации.
    """
    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


@login_required
def delete_post(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Удаление публикации.
    """
    instance = get_object_or_404(Post, pk=pk, author=request.user)
    form = PostForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:index')
    return render(
        request, 'blog/create.html', context
    )


@login_required
def add_comment(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Добавление комментария.
    """
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)


@login_required
def edit_comment(
    request: HttpRequest, pk: int, comment_id: int
) -> HttpResponse:
    """
    Редактирование комментария.
    """
    comment = get_object_or_404(Comment, pk=comment_id, author=request.user)
    if comment.author != request.user:
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': pk}
        )
    form = CommentForm(request.POST or None, instance=comment)
    context = {
        'form': form,
        'comment': comment
    }
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', pk=pk)
    return render(
        request, 'blog/comment.html', context
    )


@login_required
def delete_comment(
    request: HttpRequest, pk: int, comment_id: int
) -> HttpResponse:
    """
    Удаление комментария.
    """
    comment = get_object_or_404(
        Comment, pk=comment_id
    )
    if comment.author != request.user:
        return redirect('blog:post_detail', pk=pk)
    context = {'comment': comment}
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', pk=pk)
    return render(
        request, 'blog/comment.html', context
    )
