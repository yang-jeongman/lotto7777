from django import forms
from .models import Post, Comment

INPUT_CLASS = 'w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:border-lotto-gold focus:ring-1 focus:ring-lotto-gold'


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': '제목을 입력하세요',
            }),
            'content': forms.Textarea(attrs={
                'class': INPUT_CLASS,
                'placeholder': '내용을 입력하세요',
                'rows': 10,
            }),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': INPUT_CLASS,
                'placeholder': '댓글을 입력하세요',
                'rows': 3,
            }),
        }
