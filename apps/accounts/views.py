from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView

from .forms import SignupForm, LoginForm
from .models import LoginHistory


class SignupView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('landing:index')
        return render(request, 'accounts/signup.html', {'form': SignupForm()})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('landing:index')
        return render(request, 'accounts/signup.html', {'form': form})


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('landing:index')
        return render(request, 'accounts/login.html', {'form': LoginForm()})

    def post(self, request):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            LoginHistory.objects.create(
                user=user,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:300],
            )
            return redirect('landing:index')
        return render(request, 'accounts/login.html', {'form': form})


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('landing:index')


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['profile'] = getattr(user, 'profile', None)
        context['login_history'] = user.login_history.all()[:20]
        try:
            from apps.community.models import Post, Comment
            context['post_count'] = Post.objects.filter(author=user).count()
            context['comment_count'] = Comment.objects.filter(author=user).count()
        except Exception:
            context['post_count'] = 0
            context['comment_count'] = 0
        return context
