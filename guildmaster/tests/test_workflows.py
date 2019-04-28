import secrets

import pytest
import requests

from guildmaster import exceptions, models
from guildmaster.workflows import AuthorizationCodeWorkflow


def test_authorization_response_state(rf, tf_client, settings):
    data = {'code': secrets.token_urlsafe(16), 'state': secrets.token_urlsafe(16)}
    flow = AuthorizationCodeWorkflow(tf_client.name)
    request = rf.get('/auth/token', data=data)
    request.session[settings.GUILDMASTER_SESSION_STATE_KEY] = data['state']
    flow.validate_state(request)
    request.session[settings.GUILDMASTER_SESSION_STATE_KEY] = secrets.token_hex(16)
    with pytest.raises(ValueError):
        flow.validate_state(request)


def test_authorization_response_error(rf, tf_client, settings):
    data = {
        'error': 'temporarily_unavailable',
        'error_description': 'server offline for maintenance',
        'error_uri': 'https://tools.ietf.org/html/rfc6749#section-4.1.2',
        'state': secrets.token_urlsafe(16),
    }
    flow = AuthorizationCodeWorkflow(tf_client.name)
    request = rf.get('/auth/token', data=data)
    request.session[settings.GUILDMASTER_SESSION_STATE_KEY] = data['state']
    with pytest.raises(exceptions.OAuth2Error) as exc:
        flow.validate_authorization_response(request)
    assert str(exc.value) == (
        'temporarily_unavailable: server offline for maintenance ' '(https://tools.ietf.org/html/rfc6749#section-4.1.2)'
    )
    assert exc.value.error == data['error']
    assert exc.value.description == data['error_description']
    assert exc.value.uri == data['error_uri']


def test_fetch_token(rf, tf_client, requests_mock, tf_token_response, tf_datestr, tf_user):
    requests_mock.post(tf_client.token_url, json=tf_token_response, headers={'Date': tf_datestr})
    data = {'code': secrets.token_urlsafe(16), 'state': secrets.token_urlsafe(16)}
    flow = AuthorizationCodeWorkflow(tf_client.name)
    request = rf.get('/auth/token', username=tf_user, data=data)
    token = flow.get_access_token(request)
    assert isinstance(token, models.Token)
    assert token.access_token == tf_token_response['access_token']


def test_fetch_token_auth_error(rf, tf_client, requests_mock, tf_token_response, tf_datestr, tf_user):
    error = {
        'error': 'temporarily_unavailable',
        'error_description': 'server offline for maintenance',
        'error_uri': 'https://tools.ietf.org/html/rfc6749#section-4.1.2',
        'state': secrets.token_urlsafe(16),
    }
    requests_mock.post(tf_client.token_url, json=error)
    data = {'code': secrets.token_urlsafe(16), 'state': secrets.token_urlsafe(16)}
    flow = AuthorizationCodeWorkflow(tf_client.name)
    request = rf.get('/auth/token', username=tf_user, data=data)
    with pytest.raises(exceptions.OAuth2Error) as exc:
        flow.get_access_token(request)
    assert str(exc.value) == (
        'temporarily_unavailable: server offline for maintenance ' '(https://tools.ietf.org/html/rfc6749#section-4.1.2)'
    )
    assert exc.value.error == error['error']
    assert exc.value.description == error['error_description']
    assert exc.value.uri == error['error_uri']


def test_fetch_token_auth_failure(rf, tf_client, requests_mock, tf_token_response, tf_datestr, tf_user):
    requests_mock.post(tf_client.token_url, exc=requests.ConnectionError())
    data = {'code': secrets.token_urlsafe(16), 'state': secrets.token_urlsafe(16)}
    flow = AuthorizationCodeWorkflow(tf_client.name)
    request = rf.get('/auth/token', username=tf_user, data=data)
    with pytest.raises(IOError):
        flow.get_access_token(request)
