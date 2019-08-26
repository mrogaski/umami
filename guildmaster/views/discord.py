from django import http
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.http import urlencode
from django.views import View
from django.views.generic import ListView

from guildmaster.models import Client, DiscordAccount, DiscordProvider, Token
from guildmaster.requests import TokenAuth


class DiscordAccountSync(LoginRequiredMixin, View):
    provider = DiscordProvider

    def get(self, request):
        try:
            client = Client.objects.get(provider_id=self.provider.name)
        except Client.DoesNotExist:
            messages.error(request, f"No client configured for {self.provider.description}")
            return http.HttpResponseRedirect(reverse('guildmaster:discord-list'))

        try:
            token = Token.objects.get(client=client, user=request.user)
        except Token.DoesNotExist:
            auth_url = '{}?{}'.format(
                reverse('guildmaster:authorization', kwargs={'client_name': self.provider.name}),
                urlencode({settings.GUILDMASTER_RETURN_FIELD_NAME: reverse('guildmaster:discord-sync')}),
            )
            return http.HttpResponseRedirect(auth_url)

        auth = TokenAuth(token)
        try:
            account = DiscordAccount.objects.synchronize(request.user, token)
        except IOError as exc:
            messages.error(f"Unable to communicate with {self.provider.description}: {exc}")
            return http.HttpResponseRedirect(reverse('guildmaster:discord-list'))

        messages.success(request, f"Synchronized {self.provider.description} account: {account}")
        return http.HttpResponseRedirect(reverse('guildmaster:discord-list'))


class DiscordAccountList(LoginRequiredMixin, ListView):
    model = DiscordAccount

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(users=self.request.user)