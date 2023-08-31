import os.path

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormMixin
from django.views.generic.list import MultipleObjectMixin
from pytils.translit import slugify
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView

from .forms import *
from .utils import *


class MainPage(ListView):
    template_name = 'BaseApp/index.html'
    model = Post
    context_object_name = 'posts'
    paginate_by = 2
    extra_context = {
        'title': 'Главная'
    }

    def get_queryset(self):
        posts_qs = cache.get('posts_qs')
        if not posts_qs:
            posts_qs = Post.objects.select_related('user__profile').prefetch_related('comments_posts', 'rating').all()
            cache.set('posts_qs', posts_qs, 60*10)
        return posts_qs


class PostDetailView(FormMixin, SuccessMessageMixin, DetailView, MultipleObjectMixin):
    model = Post
    template_name = 'BaseApp/post_detail.html'
    context_object_name = 'post_view'
    slug_url_kwarg = 'post_view_slug'
    form_class = CommentForm
    success_message = 'Комментарий добавлен'
    paginate_by = 8

    def get_queryset(self):
        queryset = Post.objects.select_related('user__profile').filter(slug=self.kwargs['post_view_slug'])
        return queryset

    def get_success_url(self, **kwargs):
        return reverse_lazy('post_view', kwargs={'post_view_slug': self.get_object().slug})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid:
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.post = self.get_object()
        self.object.author = self.request.user.profile
        self.object.save()
        return super().form_valid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        object_list = Comments.objects.select_related('author').filter(post__slug=self.kwargs['post_view_slug'])
        context = super().get_context_data(object_list=object_list, **kwargs)
        current_post = get_object_or_404(Post, slug=self.kwargs['post_view_slug'])
        rating_count = current_post.total_rating()
        rating_status = False
        if current_post.rating.filter(id=self.request.user.id):
            rating_status = True
        comm_count = len(object_list)
        context['title'] = context['post_view']
        context['rating_count'] = rating_count
        context['comm_count'] = comm_count
        context['rating_status'] = rating_status
        return context


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('home')
    context_object_name = 'post_delete'
    template_name = 'BaseApp/post_delete.html'
    slug_url_kwarg = 'post_view_slug'
    extra_context = {
        'title': 'Удаление поста'
    }
    success_message = 'СТАТЬЯ УДАЛЕНА'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.user:
            return True
        return False


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Post
    form_class = AddPostForm
    context_object_name = 'post_update'
    template_name = 'BaseApp/post_update.html'
    slug_url_kwarg = 'post_view_slug'
    extra_context = {
        'title': 'Обновление поста'
    }
    success_url = '/'
    success_message = 'СТАТЬЯ ОБНОВЛЕНА'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.user:
            return True
        return False


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'BaseApp/register.html'
    extra_context = {
        'title': 'Регистрация'
    }

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('profile_redirect')


class UserLoginView(SuccessMessageMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'BaseApp/login.html'
    extra_context = {
        'title': 'Логин'
    }


class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'BaseApp/profile.html'
    context_object_name = 'profile_fields'
    pk_url_kwarg = 'profile_id'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Профиль {self.request.user}'
        return context


class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = User
    success_url = reverse_lazy('home')
    context_object_name = 'user_delete'
    template_name = 'BaseApp/user_delete.html'
    pk_url_kwarg = 'pk'
    extra_context = {
        'title': 'УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ'
    }
    success_message = 'ПОЛЬЗОВАТЕЛЬ УДАЛЁН'

    def test_func(self):
        user = self.get_object()
        if self.request.user == user:
            return True
        return False


class CommentDelete(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Comments
    context_object_name = 'comment_delete'
    template_name = 'BaseApp/comment_delete.html'
    pk_url_kwarg = 'pk'
    extra_context = {
        'title': 'Удаление комментария'
    }
    success_message = 'Комментарий удалён'

    def get_success_url(self):
        comment_slug = self.get_object()
        return reverse('post_view', kwargs={'post_view_slug': comment_slug.post.slug})

    def test_func(self):
        comment_profile = self.get_object()
        if (self.request.user.profile == comment_profile.author) or\
                (self.request.user == comment_profile.post.user):
            return True
        return False


class CommentUpdate(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Comments
    form_class = CommentForm
    context_object_name = 'comment_update'
    template_name = 'BaseApp/comment_update.html'
    slug_url_kwarg = 'post_view_slug'
    pk_url_kwarg = 'pk'
    extra_context = {
        'title': 'Обновление комментария'
    }
    success_message = 'Комментарий обновлён'

    def get_success_url(self):
        comment_slug = self.get_object()
        return reverse('post_view', kwargs={'post_view_slug': comment_slug.post.slug})

    def test_func(self):
        comment_profile = self.get_object()
        if self.request.user.profile == comment_profile.author:
            return True
        return False


class PasswordsChangeView(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    form_class = PasswordsChangeForm
    template_name = 'BaseApp/password_change.html'
    success_url = reverse_lazy('home')
    success_message = 'Пароль изменён'


class RatedPages(LoginRequiredMixin, ListView):
    template_name = 'BaseApp/rated_posts.html'
    model = Post
    context_object_name = 'rated_posts'
    paginate_by = 4
    extra_context = {
        'title': 'Оценённые статьи'
    }

    def get_queryset(self):
        posts_rated_qs = cache.get('posts_rated_qs')
        if not posts_rated_qs:
            posts_rated_qs = Post.objects.select_related('user', 'user__profile').filter(rating=self.request.user)
            cache.set('posts_rated_qs', posts_rated_qs, 60 * 10)
        return posts_rated_qs


class UserPosts(LoginRequiredMixin, ListView):
    template_name = 'BaseApp/user_posts.html'
    model = Post
    context_object_name = 'user_posts'
    paginate_by = 4
    extra_context = {
        'title': 'Статьи пользователя'
    }

    def get_queryset(self):
        user_posts = cache.get('user_posts')
        if not user_posts:
            user_posts = Post.objects.select_related('user', 'user__profile').filter(user=self.request.user)
            cache.set('user_posts', user_posts, 60 * 10)
        return user_posts


@login_required
def rating_view(request, post_view_slug):
    post = get_object_or_404(Post, slug=request.POST.get('post_slug'))
    if post.rating.filter(id=request.user.id).exists():
        post.rating.remove(request.user)
    else:
        post.rating.add(request.user)
    return HttpResponseRedirect(reverse('post_view', args=[post_view_slug]))


def logout_user(request):
    logout(request)
    return redirect('home')


def profile(request):
    # Profile redirect
    if request.user.is_authenticated:
        return redirect(request.user.profile.get_absolute_url())
    return redirect('home')


@login_required
def adding_post(request):
    # Combines three forms, one of which is repeated three times, and also limits the number of posts
    PhotosFormSet = modelformset_factory(PostPhotos,
                                         form=AddPhotoForm, extra=3)

    if request.method == 'POST':
        # The following check is implemented for the constraint
        if Post.objects.filter(user_id=request.user).count() < 3:
            postForm = AddPostForm(request.POST)
            formset = PhotosFormSet(request.POST, request.FILES, queryset=PostPhotos.objects.none())

            if postForm.is_valid() and formset.is_valid():
                post_form = postForm.save(commit=False)
                post_form.user = request.user
                # Slug attribute formation
                post_form.slug = slugify(post_form.title)
                post_form.save()

                for form in formset.cleaned_data:
                    if form:
                        image = form['image']
                        photo = PostPhotos(post=post_form, image=image)
                        photo.save()

                messages.success(request, 'СТАТЬЯ ДОБАВЛЕНА')
                return HttpResponseRedirect('/')
        else:
            messages.error(request, 'КОЛИЧЕСТВО СТАТЕЙ ОГРАНИЧЕНО! МАКСИМУМ: 3')
            return HttpResponseRedirect('/')
    else:
        postForm = AddPostForm()
        formset = PhotosFormSet(queryset=PostPhotos.objects.none())
    return render(request, 'BaseApp/add_post.html', {'postForm': postForm,
                                                     'formset': formset,
                                                     'title': "Добавить пост"})


@login_required
def user_updating_view(request):
    title = 'Обновление профиля'
    user = get_object_or_404(User, id=request.user.id)
    u_profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        user_update = UserUpdateForm(request.POST, instance=user)
        profile_update = ProfileUpdateForm(request.POST, request.FILES, instance=u_profile)

        if user_update.is_valid() and profile_update.is_valid():
            user.email = user_update.cleaned_data['email']
            user.save()

            pic_name = str(Profile.objects.get(user=request.user).profile_pic)
            if os.path.exists(os.path.join(settings.MEDIA_ROOT, pic_name)):
                u_profile.profile_pic = profile_update.cleaned_data['profile_pic']
                os.remove(os.path.join(settings.MEDIA_ROOT, pic_name))
            else:
                u_profile.profile_pic = profile_update.cleaned_data['profile_pic']
            u_profile.nick_name = profile_update.cleaned_data['nick_name']
            u_profile.save()

            messages.success(request, 'Профиль обновлён')
            return redirect('profile_redirect')
    else:
        user_update = UserUpdateForm(instance=user)
        profile_update = ProfileUpdateForm(instance=u_profile)
    return render(request, 'BaseApp/profile_update.html', {'user_update': user_update,
                                                           'profile_update': profile_update,
                                                           'title': title})


def about(request):
    return render(request, 'BaseApp/about.html', {'title': 'О сайте'})


def contacts(request):
    return render(request, 'BaseApp/contacts.html', {'title': 'Контакты'})


def go_github(request):
    return redirect('https://github.com/IlyaMk815')


def page_not_found(request, exception):
    return HttpResponseNotFound('<h2>Страница не найдена</h2>')
