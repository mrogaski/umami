import abc
from typing import Optional


class Provider(abc.ABC):
    """Base class for provider classes that provides a registry."""

    registry = {}
    base_url = None
    revocation_url = None
    verification_url = None
    default_scopes = ()
    http_basic_auth = False

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.name in cls.registry:
            raise AttributeError(f"{cls.name} already in use by {cls.registry[cls.name]}")
        cls.registry[cls.name] = cls

    def __str__(self):
        return self.name

    @property
    @abc.abstractmethod
    def name(self) -> Optional[str]:
        pass

    @property
    @abc.abstractmethod
    def description(self) -> Optional[str]:
        pass

    @property
    @abc.abstractmethod
    def base_url(self) -> Optional[str]:
        pass

    @property
    @abc.abstractmethod
    def authorization_url(self) -> Optional[str]:
        pass

    @property
    @abc.abstractmethod
    def token_url(self) -> Optional[str]:
        pass

    @property
    @abc.abstractmethod
    def userinfo_url(self) -> Optional[str]:
        pass

    @classmethod
    @abc.abstractmethod
    def resource(cls, data: dict) -> str:
        pass

    @classmethod
    def choices(cls):
        return [(k, v.description) for k, v in cls.registry.items()]


class DiscordProvider(Provider):
    """A provider for Discord, https://discordapp.com/ ."""

    name = 'discord'
    description = 'Discord'
    base_url = 'https://discordapp.com/api'
    authorization_url = 'https://discordapp.com/api/oauth2/authorize'
    token_url = 'https://discordapp.com/api/oauth2/token'
    userinfo_url = 'https://discordapp.com/api/users/@me'
    revocation_url = 'https://discordapp.com/api/oauth2/token/revoke'
    default_scopes = ('identify', 'email')

    @classmethod
    def resource(cls, data: dict) -> str:
        return data.get('username') + "#" + data.get('discriminator')


class BattleNetProvider(Provider):
    """A provider for Battle.net (US), https://develop.battle.net/ ."""

    name = 'battle-net'
    description = 'Battle.net'
    base_url = 'https://us.api.battle.net'
    authorization_url = 'https://us.battle.net/oauth/authorize'
    token_url = 'https://us.battle.net/oauth/token'
    userinfo_url = 'https://us.battle.net/oauth/userinfo'
    verification_url = 'https://us.battle.net/oauth/check_token'
    default_scopes = ('openid', 'wow.profile')

    @classmethod
    def resource(cls, data: dict) -> str:
        return data.get('battletag')
