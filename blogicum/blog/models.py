from core.models import DateTimeModel, PublishedModel
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from .constants import MAX_FIELD_LENGTH

User = get_user_model()


class Category(DateTimeModel, PublishedModel):
    """
    Модель "Категории".
    Содержит данные о
    категориях публикаций.
    """
    title = models.CharField('Заголовок', max_length=MAX_FIELD_LENGTH)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text='Идентификатор страницы для URL; '
        'разрешены символы латиницы, цифры, дефис и подчёркивание.')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(DateTimeModel, PublishedModel):
    """
    Модель "Местоположения".
    Содержит данные о локациях
    сделанных публикаций.
    """
    name = models.CharField('Название места', max_length=MAX_FIELD_LENGTH)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(DateTimeModel, PublishedModel):
    """
    Модель "Публикации".
    Содержит данные
    добавленных публикаций.
    """
    title = models.CharField('Заголовок', max_length=MAX_FIELD_LENGTH)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text='Если установить дату и время в будущем '
        '— можно делать отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name='posts',
        verbose_name='Категория'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Местоположение',
    )
    image = models.ImageField(
        'Фото', blank=True, upload_to='post_images'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'title', 'author'
                ),
                name='Limiting the uniqueness of a publication',
            ),
        )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.pk})


class Comment(DateTimeModel):
    """
    Модель "Комментарии".
    Содержит данные о комментариях
    пользователей к опубликованным
    публикациям других авторов.
    """
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
