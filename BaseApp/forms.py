from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import *


class AddPostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Post
        fields = ['title', 'content',]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form_input'}),
            'content': forms.Textarea(attrs={'cols': 50, 'rows': 5, 'class': 'form_input'}),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 200:
            raise ValidationError('Длина превышает 200 символов')
        return title

    def clean_content(self):
        content = self.cleaned_data['content']
        if len(content) > 2056:
            raise ValidationError('Длинна статьи больше 2056 символов')
        return content


class AddPhotoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = PostPhotos
        fields = ['image', ]


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form_input'}))
    email = forms.EmailField(label='@Email', widget=forms.EmailInput(attrs={'class': 'form_input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form_input'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form_input'}))
    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class PasswordsChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Старый пароль', widget=forms.PasswordInput(attrs={'class': 'form_input'}))
    new_password1 = forms.CharField(label='Новый пароль', widget=forms.PasswordInput(attrs={'class': 'form_input'}))
    new_password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form_input'}))
    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.TextInput(attrs={'class': 'form_input', 'label': 'Email'}),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nick_name', 'profile_pic']
        widgets = {
            'nick_name': forms.TextInput(attrs={'class': 'form_input'}),
            'profile_pic': forms.FileInput(attrs={'class': 'form_input'})
        }


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'input_field'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'input_field'}))


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'cols': 50, 'rows': 5, 'class': 'form_input'}),
        }

    def clean_text(self):
        text = self.cleaned_data['text']
        if len(text) > 2193:
            raise ValidationError('Длинна комментария больше 15 символов')
        return text
