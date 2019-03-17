from django.conf import settings
from django.urls import path

from guildmaster import views

app_name = 'guildmaster'
urlpatterns = [
    path('authorize/<slug:client_name>', views.AuthorizationView.as_view(), name='authorize'),
    path('token/<slug:client_name>', views.TokenView.as_view(), name='token'),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + [path('dump', views.ClientDumpView.as_view(), name='dump')]
