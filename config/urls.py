"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin URLs
    path('admin/core/', include('core.urls')),
    path('admin/hr/', include('hr.urls')),
    path('admin/zktest/', include('zktest.urls')),
    path('admin/', admin.site.urls),
    
    # ADMS + API + Mobile (all in one - priority order matters!)
    path('', include('zktest.api.urls')),  # ADMS: /iclock/*, API: /api/*, PyZK: /api/pyzk/*
    path('', include('zktest.urls')),      # Mobile: /mobile/*, Reports: /reports/*
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
