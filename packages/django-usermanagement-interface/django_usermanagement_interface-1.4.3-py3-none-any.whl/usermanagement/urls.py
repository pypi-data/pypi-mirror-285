from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from usermanagement import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
]

urlpatterns += [path("user-management/", include("usermanagement.core.urls"))]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)