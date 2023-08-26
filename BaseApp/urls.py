from django.urls import path
from django.views.decorators.cache import cache_page

from .views import *

urlpatterns = [
    path('', MainPage.as_view(), name='home'),
    path('GitHub/', go_github, name='GitHub'),
    path('contacts/', contacts, name='contacts'),
    path('about/', about, name='about'),
    path('add_post/', adding_post, name='add_post'),
    path('post_view/<slug:post_view_slug>/', PostDetailView.as_view(), name='post_view'),
    path('post_update/<slug:post_view_slug>/', PostUpdateView.as_view(), name='post_update'),
    path('post_delete/<slug:post_view_slug>/', PostDeleteView.as_view(), name='post_delete'),
    path('profile/', profile, name='profile_redirect'),
    path('profile/id<int:profile_id>/', ProfileView.as_view(), name='profile'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('logout/', logout_user, name='logout'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile_update/', user_updating_view, name='profile_update_form'),
    path('user_delete/<int:pk>', UserDeleteView.as_view(), name='user_delete'),
    path('user_posts/', UserPosts.as_view(), name='user_posts'),
    path('comment_delete/<int:pk>', CommentDelete.as_view(), name='comment_delete'),
    path('comment_update/<int:pk>', CommentUpdate.as_view(), name='comment_update'),
    path('password_change/', PasswordsChangeView.as_view(), name='password_change'),
    path('rating/<slug:post_view_slug>/', rating_view, name='rating_post'),
    path('rated_posts/', RatedPages.as_view(), name='rated_posts'),
]

handler404 = page_not_found
handler403 = page_not_found
