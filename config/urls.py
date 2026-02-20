from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('saju/', include('apps.saju.urls')),
    path('result/', include('apps.results.urls')),
    path('community/', include('apps.community.urls')),
    path('', include('apps.landing.urls')),
]
