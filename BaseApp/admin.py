from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'time_create', 'is_published',)
    list_display_links = ('id', 'title')
    search_fields = ('title', 'content')
    list_editable = ('is_published',)
    list_filter = ('is_published', 'time_create')
    fields = ('title', 'slug', 'content', 'is_published', 'time_create', 'time_update')
    readonly_fields = ('time_create', 'time_update')
    prepopulated_fields = {'slug': ('title',)}


class PostTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name', )}


class PostPhotosAdmin(admin.ModelAdmin):

    def get_html_photo(self, object):
        if object.image:
            return mark_safe(f"<img src='{object.image.url}' width=50>")

    get_html_photo.short_description = 'Миниатюра'


class UserProfileAdmin(admin.ModelAdmin):
    fields = ('user', 'nick_name', 'profile_pic', 'time_create', 'time_update')
    readonly_fields = ('time_create',)


admin.site.register(PostPhotos, PostPhotosAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Profile, UserProfileAdmin)
admin.site.register(Comments)

admin.site.site_title = 'Админ-панель сайта'
admin.site.site_header = 'Админ-панель сайта'
