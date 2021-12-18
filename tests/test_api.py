import os

import pytest as pytest

from goldtool.api import get_clan_id


@pytest.fixture
def api_key():
    api_key = os.getenv("WARGAMING_API_KEY", None)
    if api_key is None:
        raise ValueError('Missing API-Key!')
    yield api_key


@pytest.mark.parametrize("clan_tag, expected_clan_id",
                         [("STRGV", 500197237),
                          ("CH3SS", 500161393),
                          ("FAME", 500025989),
                          ("TENTS", 500045382),
                          ("BYOND", 500060149)])
def test_clan_id_lookup(clan_tag, expected_clan_id, api_key):
    assert get_clan_id(api_key=api_key, clan_tag=clan_tag) == expected_clan_id
