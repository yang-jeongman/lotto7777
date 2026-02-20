from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

from .models import UserProfile

INPUT_CLASS = 'w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:border-lotto-gold focus:ring-1 focus:ring-lotto-gold'


class SignupForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': '이메일 주소',
            'autocomplete': 'email',
        })
    )
    nickname = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': '닉네임 (커뮤니티에서 사용)',
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': '비밀번호',
            'autocomplete': 'new-password',
        }),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': '비밀번호 확인',
            'autocomplete': 'new-password',
        }),
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('이미 가입된 이메일입니다.')
        return email

    def clean_nickname(self):
        nickname = self.cleaned_data['nickname']
        if UserProfile.objects.filter(nickname=nickname).exists():
            raise forms.ValidationError('이미 사용 중인 닉네임입니다.')
        return nickname

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('비밀번호가 일치하지 않습니다.')
        return cleaned

    def save(self):
        email = self.cleaned_data['email']
        user = User.objects.create_user(
            username=email,
            email=email,
            password=self.cleaned_data['password1'],
        )
        UserProfile.objects.create(
            user=user,
            nickname=self.cleaned_data['nickname'],
        )
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': '이메일 주소',
            'autocomplete': 'email',
        }),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': '비밀번호',
            'autocomplete': 'current-password',
        }),
    )
