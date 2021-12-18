import os
import time

import pytest as pytest

from goldtool.api import get_clan_id, get_season, get_player_from_clan, get_season_battles, get_request
from goldtool.util import InvalidAPIKeyException, Season, MissingResultException, ClanMember, APIException


@pytest.fixture
def api_key():
    api_key = os.getenv("WARGAMING_API_KEY", None)
    if api_key is None:
        raise ValueError('Missing API-Key!')
    yield api_key
    time.sleep(0.5)


def test_get_request_no_fail():
    with pytest.raises(APIException) as api_exc:
        get_request('test_endpoint')
    assert str(api_exc.value) == "METHOD_NOT_FOUND"


def test_exception_on_invalid_apikey():
    with pytest.raises(InvalidAPIKeyException):
        get_clan_id("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "STRGV")


@pytest.mark.parametrize("clan_tag, expected_clan_id",
                         [("STRGV", 500197237),
                          ("CH3SS", 500161393),
                          ("FAME", 500025989),
                          ("TENTS", 500045382),
                          ("BYOND", 500060149)])
def test_clan_id_lookup(clan_tag, expected_clan_id, api_key):
    assert expected_clan_id == get_clan_id(api_key=api_key, clan_tag=clan_tag)


@pytest.mark.parametrize("clan_tag", ['MBLE', 'XYZA'])
def test_exception_clan_id_lookup(clan_tag, api_key):
    with pytest.raises(MissingResultException) as me_exception:
        get_clan_id(api_key=api_key, clan_tag=clan_tag)
    assert str(me_exception.value) == f'No result found for clan tag {clan_tag}.'


@pytest.mark.parametrize("season_id", ["season_17", "thunderstorm_season", "season_16"])
def test_get_seasons(season_id, api_key):
    test_season = Season(name=season_id, id=season_id)
    assert test_season in get_season(api_key)


@pytest.mark.parametrize("player_id, clan_id",
                         [(511218795, 500197237),
                          (524446673, 500161393),
                          (511199787, 500013252),
                          (500241816, 500013252)])
def test_get_player_from_clan(player_id, clan_id, api_key):
    result = get_player_from_clan(api_key=api_key, clan_id=clan_id)
    assert player_id in {player.id for player in result}


@pytest.mark.parametrize("player_id, season_id, expected_8, expected_10",
                         [(511218795, "season_17", 0, 30),
                          (524446673, "season_17", 8, 63),
                          (511199787, "season_17", 0, 0),
                          (500241816, "season_17", 0, 0)])
def test_get_season_battles_player(player_id, season_id, expected_8, expected_10, api_key):
    test_member = ClanMember(name="XXXXX", id=player_id)
    get_season_battles(api_key=api_key, clan_member=[test_member], season_id=season_id)
    assert expected_8 == test_member.t8
    assert expected_10 == test_member.t10
