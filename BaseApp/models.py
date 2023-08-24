from PIL import Image
from django.conf import settings
from django.db import models
from django.urls import reverse


# Creating the path for profile picture
def picture_path(instance, filename):
    return 'profile_pics/{0}/{1}'.format(instance.user, filename)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    nick_name = models.CharField(max_length=16, verbose_name='Никнейм')
    profile_pic = models.ImageField(upload_to=picture_path, verbose_name='Фото профиля')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Время изменения')

    def get_absolute_url(self):
        return reverse('profile', kwargs={'profile_id': self.pk})

    def __str__(self):
        return self.user

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save()

        img = Image.open(self.profile_pic.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.profile_pic.path)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-time_update']


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    title = models.CharField(max_length=255, verbose_name='Название')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='URL')
    content = models.TextField(blank=True, verbose_name='Контент')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    is_published = models.BooleanField(default=True, verbose_name='Публикация')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Время изменения')
    rating = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='posts_rating')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_view', kwargs={'post_view_slug': self.slug})

    def total_rating(self):
        return self.rating.count()

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ['-time_update']


class PostPhotos(models.Model):
    image = models.ImageField(upload_to='photos/%Y/%m/%d', verbose_name='Фото', max_length=100)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, verbose_name='Изображение')

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображении'


class Comments(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='Статья', blank=True,
                             null=True, related_name='comments_posts')
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='Автор комментария', blank=True,
                               null=True)
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Время изменения')
    text = models.TextField(max_length=2192, blank=True, verbose_name='Комментарий')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-time_update']

