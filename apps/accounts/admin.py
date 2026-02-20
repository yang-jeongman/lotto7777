from django.contrib import admin
from .models import UserProfile, LoginHistory


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['nickname', 'user', 'created_at']
    search_fields = ['nickname', 'user__email']


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'logged_in_at']
    list_filter = ['logged_in_at']
    readonly_fields = ['user', 'ip_address', 'user_agent', 'logged_in_at']
