from django import forms

from .models import Comment, Post, User


class FormCleanMixin:
    """
    Миксин для очистки
    данных из форм.
    """
    def clean(self):
        super().clean()


class PostForm(FormCleanMixin, forms.ModelForm):
    """
    Форма для добавления новых публикаций.
    """
    class Meta:
        model = Post
        exclude = (
            'author', 'is_published'
        )
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class UserForm(FormCleanMixin, forms.ModelForm):
    """
    Форма для редактирования профиля.
    """
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email'
        )


class CommentForm(FormCleanMixin, forms.ModelForm):
    """
    Форма для отправки комментариев.
    """
    class Meta:
        model = Comment
        fields = ('text',)
