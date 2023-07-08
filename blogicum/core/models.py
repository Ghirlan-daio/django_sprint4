from django.db import models


class DateTimeModel(models.Model):
    """
    Абстрактная модель.
    Добавляет к модели дату создания.
    """
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        abstract = True


class PublishedModel(models.Model):
    """
    Абстрактная модель.
    Добавляет к модели данные о
    состоянии контента (опубликовано/не опубликовано).
    """
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.')

    class Meta:
        abstract = True
