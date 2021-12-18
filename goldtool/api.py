import time

from typing import List, Dict

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from goldtool.util import ClanMember, InvalidAPIKeyException, Season, MissingResultException, export_to_excel

BASE_URL = "https://api.worldoftanks.eu/wot"


def get_session() -> requests.Session:
    """
    Returns a session with integrated retry adapter.
    :return: session object
    """
    adapter = HTTPAdapter(max_retries=Retry(total=3))
    req_session = requests.Session()
    req_session.mount("https://", adapter)
    req_session.mount("http://", adapter)
    return req_session


def get_request(endpoint: str, params: Dict[str, str] = None, fields: List[str] = None):
    url = f'{BASE_URL}//{endpoint}//'
    if params:
        for param, param_value in params.items():
            url += f'{"&" if "?" in url else "?"}{param}={param_value}'

    if fields:
        url += f'{ "&" if "?" in url else "?"}fields={"%2C+".join(fields)}'

    with get_session() as session:
        response = session.get(url)

    response.encoding = "utf-8"
    response.raise_for_status()
    try:
        json_response = response.json()
    except Exception as e:
        print(e)
        return response.text

    if json_response['status'] == 'error' and json_response['error']['message'] == 'INVALID_APPLICATION_ID':
        raise InvalidAPIKeyException(json_response['error']['message'])
    return json_response['data']


def get_season(api_key: str) -> List[Season]:
    response = get_request('globalmap/seasons', params={'application_id': api_key}, fields=['season_name', 'season_id'])
    return [Season(name=season['season_name'], id=season['season_id']) for season in response]


def get_clan_id(api_key: str, clan_tag: str) -> int:
    params = {'application_id': api_key, 'search': clan_tag}
    response = get_request('/clans/list', params=params, fields=['tag', 'clan_id'])
    filtered_result = list(filter(lambda result: result['tag'] == clan_tag, response))
    if len(filtered_result) != 1:
        raise MissingResultException(f'No result found for clan tag {clan_tag}.')
    return filtered_result[0]['clan_id']


def get_player_from_clan(api_key: str, clan_id: int) -> List[ClanMember]:
    params = {'application_id': api_key, 'clan_id': clan_id}
    response = get_request('/clans/info', params=params, fields=['members.account_id', 'members.account_name'])
    return [ClanMember(name=member['account_name'], id=member['account_id'])
            for member in response[str(clan_id)]['members']]


def get_season_battles(api_key: str, clan_member: List[ClanMember], season_id: str) -> List[ClanMember]:
    fields = ['seasons.battles', 'seasons.vehicle_level']
    for member in clan_member:
        params = {'application_id': api_key, 'season_id': season_id,
                  'account_id': member.id, 'vehicle_level': '10%2C+8'}
        response = get_request('/globalmap/seasonaccountinfo', params=params, fields=fields)

        season_battles = response[str(member.id)]['seasons'][season_id]
        t10_battles = season_battles[0]['battles']
        t8_battles = season_battles[1]['battles']
        member.t10 = t10_battles if t10_battles is not None else 0
        member.t8 = t8_battles if t8_battles is not None else 0
        time.sleep(0.5)
    return clan_member


def test_run():


    clan_id = get_clan_id(api_key=api_key, clan_tag=clan_tag)
    clan_member = get_player_from_clan(api_key=api_key, clan_id=clan_id)
    clan_member = get_season_battles(api_key=api_key, clan_member=clan_member, season_id=season_id)
    export_to_excel(clan_member)


test_run()
