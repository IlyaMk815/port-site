from django import template
from django.core.cache import cache
from django.db.models import Count

from BaseApp.models import *

YA_END = [2, 3, 4]

register = template.Library()


@register.simple_tag()
def get_posts_photos(filter=None):
    """
    Returns a list of photos associated with a post
    """
    photos = PostPhotos.objects.select_related('post').filter(post_id=filter)
    return photos


@register.simple_tag()
def get_photos_count(filter=None):
    p_photos = PostPhotos.objects.select_related('post').filter(post_id=filter).count()
    return p_photos


@register.simple_tag()
def get_first_3():
    """
    Returns a list of the first three posts by rating
    """
    top = cache.get('top')
    if not top:
        top = Post.objects.only('slug', 'title').annotate(top_rait=Count('rating')).order_by('-top_rait')[:3]
        cache.set('top', top, 60*5)
    return top


@register.simple_tag()
def comm_word(count=None):
    """
    Takes a value, and if it matches an int, returns
    declension of the word 'comment' according to the last digit of the number
    """

    if type(count) is int:
        count_int = count
    else:
        count_int = 0

    count_last_digit = int((str(count_int)[-1]))

    if count_last_digit == 1:
        return 'комментарий'
    elif count_last_digit in YA_END:
        return 'комментария'
    else:
        return 'комментариев'

