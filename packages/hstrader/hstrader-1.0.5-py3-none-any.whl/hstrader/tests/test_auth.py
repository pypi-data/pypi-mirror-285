from . import client, CLIENT_ID, SECRET
from hstrader import HsTrader
import pytest


def test_login():
    response = HsTrader(CLIENT_ID, SECRET).login(CLIENT_ID, SECRET)
    assert response.access_token is not None
    assert response.refresh_token is not None
    assert response.expires_in is not None
    assert response.session_id is not None
    assert response.account_id is not None
    assert response.scope is not None
    assert response.ip_address is not None


def test_refresh_token(client: HsTrader):
    response = client.refresh_token()
    assert response.access_token is not None
    assert response.refresh_token is not None
    assert response.expires_in is not None
    assert response.session_id is not None
    assert response.account_id is not None
    assert response.scope is not None
    assert response.ip_address is not None


def test_logout(client: HsTrader):
    client.logout()
