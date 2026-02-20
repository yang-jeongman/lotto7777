from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    nickname = models.CharField(max_length=30, unique=True, verbose_name='닉네임')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '회원 프로필'
        verbose_name_plural = '회원 프로필'

    def __str__(self):
        return self.nickname


class LoginHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='login_history',
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True, default='')
    logged_in_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-logged_in_at']
        verbose_name = '접속 이력'
        verbose_name_plural = '접속 이력'

    def __str__(self):
        return f'{self.user.username} - {self.logged_in_at:%Y-%m-%d %H:%M}'
