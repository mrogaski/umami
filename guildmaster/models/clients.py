import logging
import uuid
from typing import List, Type

import jsonfield
import requests
from concurrency.fields import AutoIncVersionField
from django import http
from django.conf import settings
from django.db import models
from django.db.models.base import ModelBase
from django.utils.translation import ugettext_lazy as _
from furl import furl

from guildmaster.models import TokenBinding
from guildmaster.utils import generate_state

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ClientAdapterRegistry(ModelBase):
    """A client subclass registry implemented as a metaclass."""

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)
        if not hasattr(cls, '_registry'):
            cls._registry = {}
        else:
            if cls.adapter_id in cls._registry:
                raise ValueError('duplicate adapter type: {}'.format(cls.adapter_id))
            cls._registry[cls.adapter_id] = cls

    def _adapter_class(cls, key: str) -> Type[models.Model]:
        """Map a client adapter ID to the class.

        Args:
            key: A client subclass adapter_id attribute.

        Returns: The registered client subclass.

        """
        try:
            return cls._registry[key]
        except KeyError:
            return

    @property
    def _adapter_classes(cls) -> List[Type[models.Model]]:
        """The list of adapted clients.

        Returns: All registered client subclasses.

        """
        return [cls._registry[key] for key in cls._registry]


class ClientAdapterManager(models.Manager):
    """Client adapter manager."""

    def get(self, **kwargs):
        base = super().get(**kwargs)
        try:
            cls = base._registry[base.adapter]
            return cls.objects.get(**kwargs)
        except KeyError:
            raise self.model.DoesNotExist('Invalid adapter type: {}'.format(base.adapter))


class Client(models.Model, metaclass=ClientAdapterRegistry):
    """A base class for STI that uses the adapter attribute to distinguish subclass type."""
    DISCORD = 'discord'
    BATTLE_NET = 'battle_net'
    EVE_ONLINE = 'eve_online'
    ADAPTER_CHOICES = (
        (DISCORD, 'Discord'),
        (BATTLE_NET, 'Battle.net'),
        (EVE_ONLINE, 'EVE Online')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = AutoIncVersionField()
    created = models.DateTimeField(verbose_name=_('created'), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_('modified'), auto_now=True)
    adapter = models.CharField(verbose_name=_('adapter'), max_length=50, choices=ADAPTER_CHOICES)
    name = models.CharField(verbose_name=_('name'), max_length=50)
    slug = models.SlugField(verbose_name=_('slug'), unique=True, max_length=50)
    is_enabled = models.BooleanField(verbose_name=_('is enabled'), default=True)
    client_id = models.CharField(verbose_name=_('client id'), max_length=191)
    client_secret = models.CharField(verbose_name=_('client secret'), max_length=191)
    scopes = models.ManyToManyField('ClientScope', verbose_name=_('scopes'), related_name='clients')
    options = jsonfield.JSONField(verbose_name=_('options'), blank=True, null=True)

    objects = models.Manager()
    adapters = ClientAdapterManager()

    class Meta:
        verbose_name = _('client')
        verbose_name_plural = _('clients')

    def __str__(self):
        return self.name

    @property
    def scope(self) -> str:
        return ' '.join([str(x) for x in self.scopes.all()])

    def authorization_code(self, request: Type[http.HttpRequest]) -> str:
        code = request.GET['code']
        logger.debug('extracted authorization code: %s', code)
        return code

    def authorization_redirect(self, request: Type[http.HttpRequest], redirect_uri: str, state: str = None) -> str:
        if state is None:
            state = generate_state()
        request.session[settings.GUILDMASTER_STATE_KEY] = state
        url = furl(self.authorization_url)
        url.add(args={
            'response_type': 'code',
            'client_id': self.client_id,
            'scope': self.scope,
            'redirect_uri': request.build_absolute_uri(redirect_uri),
            'state': state
        })
        return url.url

    def token_fetch(self, request: Type[http.HttpRequest], session: Type[requests.Session] = None):
        self._validate_state(request)
        token_request = self._prepare_token_request(request)
        if session is None:
            session = requests.Session()
        try:
            response = session.send(token_request)
            response.raise_for_status()
        except requests.RequestException as ex:
            logger.error('Communication error: %s', ex)
            raise
        return TokenBinding(response.json(), user=request.user, client=self)

    def _validate_state(self, request):
        try:
            rx_state = request.GET['state']
            tx_state = request.session[settings.OAUTH_STATE_KEY]
        except KeyError as ex:
            logger.error('unable to access state: %s', ex)
            raise ValueError('OAuth2 state missing')
        logger.debug('extracted state: session=%s, request=%s', tx_state, rx_state)
        if tx_state != rx_state:
            msg = 'OAuth2 state mismatch'
            logger.error(msg)
            raise ValueError(msg)

    def _prepare_token_request(self, request):
        payload = {
            'grant_type': 'authorization_code',
            'code': self.authorization_code(request),
            'redirect_uri': self.redirect_url(request),
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        prep = requests.Request('POST', self.token_url, data=payload).prepare()
        return prep


class ClientScope(models.Model):
    """OAuth2 scopes that are used to define the scope of delegated authority."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = AutoIncVersionField()
    adapter = models.CharField(verbose_name=_('adapter'), max_length=50, choices=Client.ADAPTER_CHOICES)
    name = models.CharField(verbose_name=_('name'), max_length=191)

    class Meta:
        unique_together = ('adapter', 'name')

    def __str__(self):
        return self.name
