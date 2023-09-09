from django import forms

from .models import Comment, Post, User


class PostForm(forms.ModelForm):
    """
    Форма для добавления новых публикаций.
    """
    def clean(self):
        super().clean()

    class Meta:
        model = Post
        exclude = (
            'author', 'is_published'
        )
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class UserForm(forms.ModelForm):
    """
    Форма для редактирования профиля.
    """
    def clean(self):
        super().clean()

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email'
        )


class CommentForm(forms.ModelForm):
    """
    Форма для отправки комментариев.
    """
    def clean(self):
        super().clean()

    class Meta:
        model = Comment
        fields = ('text',)
