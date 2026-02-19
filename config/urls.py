from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('saju/', include('apps.saju.urls')),
    path('', include('apps.landing.urls')),
]
