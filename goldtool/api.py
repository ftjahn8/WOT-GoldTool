"""This file contains all api connected functions for this tool."""
import time
from typing import List, Dict, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from goldtool.util import ClanMember, Season, InvalidAPIKeyException, MissingResultException


BASE_URL = "https://api.worldoftanks.eu/wot"
'''Base URL for all WOT related api calls to the wargaming api'''


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


def get_request(endpoint: str, params: Dict[str, str] = None, fields: List[str] = None) -> Any:
    """
    Executes a get request on the API with given endpoint, params and fields.
    Inspired by https://github.com/atlassian-api/atlassian-python-api.
    :param endpoint: endpoint of the api for the get request
    :param params: parameter for the get request
    :param fields: list of fields the response should be limited to
    :return: Result of the request in json form, or in case of occurring exceptions as text
    """
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
    except Exception as exc:  # pylint: broad-except
        print(exc)
        return response.text

    if json_response['status'] == 'error' and json_response['error']['message'] == 'INVALID_APPLICATION_ID':
        raise InvalidAPIKeyException(json_response['error']['message'])
    return json_response['data']


def get_season(api_key: str) -> List[Season]:
    """
    Looks up all available seasons and returns their name and id packed in an Season object.
    :param api_key: key for the api request
    :return: List of Season objects
    """
    response = get_request('globalmap/seasons', params={'application_id': api_key}, fields=['season_name', 'season_id'])
    return [Season(name=season['season_name'], id=season['season_id']) for season in response]


def get_clan_id(api_key: str, clan_tag: str) -> int:
    """
    Looks up the clan id for a clan tag. Raises an MissingResultException if no exact result was found.
    :param api_key: key for the api request
    :param clan_tag: tag of clan the id should be retrieved for
    :return: clan id (as int)
    """
    params = {'application_id': api_key, 'search': clan_tag}
    response = get_request('/clans/list', params=params, fields=['tag', 'clan_id'])
    filtered_result = list(filter(lambda result: result['tag'] == clan_tag, response))
    if len(filtered_result) != 1:
        raise MissingResultException(f'No result found for clan tag {clan_tag}.')
    return filtered_result[0]['clan_id']


def get_player_from_clan(api_key: str, clan_id: int) -> List[ClanMember]:
    """
    Returns a list of clan member objects, each representing a current member of the clan with the clan id.
    :param api_key: key for the api request
    :param clan_id: ID of the clan the members should retrieved from
    :return: List with clan members as clan member objects
    """
    params = {'application_id': api_key, 'clan_id': clan_id}
    response = get_request('/clans/info', params=params, fields=['members.account_id', 'members.account_name'])
    return [ClanMember(name=member['account_name'], id=member['account_id'])
            for member in response[str(clan_id)]['members']]


def get_season_battles(api_key: str, clan_member: List[ClanMember], season_id: str) -> List[ClanMember]:
    """
    Updates a list of clan member objects with amount of battles and season id for a specific season.
    :param api_key: key for the api request
    :param clan_member: List of clan member objects to be updated with the season data
    :param season_id: id for the season the battles should be looked up for
    :return: updated list of clan members
    """
    fields = ['seasons.battles', 'seasons.vehicle_level']
    for member in clan_member:
        params = {'application_id': api_key, 'season_id': season_id,
                  'account_id': member.id, 'vehicle_level': '10%2C+8'}
        response = get_request('/globalmap/seasonaccountinfo', params=params, fields=fields)

        # extract battles per tier
        season_battles = response[str(member.id)]['seasons'][season_id]
        t10_battles = season_battles[0]['battles']
        t8_battles = season_battles[1]['battles']

        # update dataclass object
        member.t10 = t10_battles if t10_battles is not None else 0
        member.t8 = t8_battles if t8_battles is not None else 0
        member.season_id = season_id

        # cooldown
        time.sleep(0.5)
    return clan_member
