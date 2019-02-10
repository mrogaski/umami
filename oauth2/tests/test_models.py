import datetime as dt
import secrets

import pytest
from django.utils import timezone

from oauth2 import models


@pytest.fixture()
def token_data():
    return {
        'token_type': 'bearer',
        'access_token': secrets.token_urlsafe(64),
        'refresh_token': secrets.token_urlsafe(64),
        'expires_in': 3600,
        'example_parameter': 'example_value',
    }


def test_name(tf_client):
    assert tf_client.name == 'test_client'


def test_driver(tf_client):
    driver = tf_client.driver
    assert tf_client.service == driver.name


def test_scopes(tf_client):
    driver = tf_client.driver
    assert tf_client.scopes == driver.scopes


def test_scope_override(tf_client):
    tf_client.scope_override = 'foo bar   baz '
    tf_client.save()
    assert tf_client.scopes == ('foo', 'bar', 'baz')


def test_create_resource(tf_user, tf_client):
    resource = models.Resource.objects.create(client=tf_client, key='12345', tag='Ralff')
    resource.users.add(tf_user)
    assert isinstance(resource, models.Resource)


def test_create_token(tf_user, tf_client):
    resource = models.Resource.objects.create(client=tf_client, key='12345', tag='Ralff')
    resource.users.add(tf_user)
    token = models.Token.objects.create(
        resource=resource,
        token_type='bearer',
        access_token=secrets.token_urlsafe(64),
        refresh_token=secrets.token_urlsafe(64),
        expiry=timezone.now() + dt.timedelta(seconds=3600),
        scope='email identify',
        redirect_uri='https://test.aie-guild.org/auth/token',
    )
    assert isinstance(token, models.Token)
    assert token.client == resource.client
