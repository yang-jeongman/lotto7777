from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Board, Post, PostLike
from .forms import PostForm, CommentForm


class BoardListView(ListView):
    model = Board
    template_name = 'community/board_list.html'
    context_object_name = 'boards'

    def get_queryset(self):
        return Board.objects.annotate(post_count=models.Count('posts'))


class PostListView(ListView):
    template_name = 'community/post_list.html'
    context_object_name = 'posts'
    paginate_by = 20

    def get_queryset(self):
        self.board = get_object_or_404(Board, slug=self.kwargs['board_slug'])
        return Post.objects.filter(board=self.board).select_related('author__profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['board'] = self.board
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'community/post_detail.html'
    context_object_name = 'post'

    def get_object(self):
        post = super().get_object()
        Post.objects.filter(pk=post.pk).update(views=models.F('views') + 1)
        post.views += 1
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.select_related('author__profile')
        context['comment_form'] = CommentForm()
        context['user_liked'] = (
            self.request.user.is_authenticated
            and self.object.likes.filter(user=self.request.user).exists()
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'community/post_form.html'

    def form_valid(self, form):
        board = get_object_or_404(Board, slug=self.kwargs['board_slug'])
        form.instance.author = self.request.user
        form.instance.board = board
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('community:post_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['board'] = get_object_or_404(Board, slug=self.kwargs['board_slug'])
        return context


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'community/post_form.html'

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse('community:post_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['board'] = self.object.board
        return context


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'community/post_confirm_delete.html'

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse('community:post_list', kwargs={'board_slug': self.object.board.slug})


class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
        return redirect('community:post_detail', pk=pk)


class PostLikeToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        like, created = PostLike.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
        return JsonResponse({'liked': liked, 'count': post.like_count})
