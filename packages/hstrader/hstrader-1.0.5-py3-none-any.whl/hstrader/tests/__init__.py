import pytest
from hstrader import HsTrader
import os

CLIENT_ID = os.getenv("TEST_CLIENT_ID")
SECRET = os.getenv("TEST_CLIENT_SECRET")


def test_vfx12():
    # load the environment variables
    assert CLIENT_ID is not None
    assert SECRET is not None
    assert HsTrader(CLIENT_ID, SECRET) is not None


@pytest.fixture
def unauthenticated_client() -> HsTrader:
    return HsTrader("", "")


@pytest.fixture
def client() -> HsTrader:
    hstrader = HsTrader(CLIENT_ID, SECRET)
    return hstrader


@pytest.fixture
def EURUSD_ID(
    client: HsTrader,
) -> int:
    return client.get_symbol("EURUSD").id
