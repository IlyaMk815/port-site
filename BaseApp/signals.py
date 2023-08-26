from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Profile, Post, Comments


# Automatic creation and saving of a profile during user registration with the formation of a default nickname
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        instance.profile = Profile.objects.create(user=instance,
                                                  nick_name='DefaultNickName' + str(User.objects.count()),
                                                  profile_pic='profile_pics/default/user.png')
    instance.profile.save()


# Deleting posts cache if article, or comment, created or deleted
def cache_delete():
    cache.delete('posts_qs')
    cache.delete('top3')
    cache.delete('posts_rated_qs')
    cache.delete('user_posts')


def cache_delete_on_comment():
    cache.delete('posts_qs')
    cache.delete('posts_rated_qs')
    cache.delete('user_posts')


@receiver(post_save, sender=Post)
def post_post_save(sender, instance, created, *args, **kwargs):
    cache_delete()


@receiver(post_delete, sender=Post)
def post_post_delete(sender, instance, using, *args, **kwargs):
    cache_delete()


@receiver(post_save, sender=Comments)
def post_post_save(sender, instance, created, *args, **kwargs):
    cache_delete_on_comment()


@receiver(post_delete, sender=Comments)
def post_post_delete(sender, instance, using, *args, **kwargs):
    cache_delete_on_comment()
