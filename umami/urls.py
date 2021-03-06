from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from umami import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('ext/', include('guildmaster.urls')),
    path('markdownx/', include('markdownx.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
