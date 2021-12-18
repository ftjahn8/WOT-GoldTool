from typing import List
from dataclasses import dataclass

import openpyxl


@dataclass
class ClanMember:
    name: str
    id: int
    t8: int = 0
    t10: int = 0


@dataclass(frozen=True)
class Season:
    name: str
    id: str


class APIException(Exception):
    """"""


class InvalidAPIKeyException(APIException):
    """"""


class MissingResultException(APIException):
    """"""


def export_to_excel(member: List[ClanMember]) -> None:
    column_width = {'A': 25, 'B': 10, 'C': 10, 'D': 10, 'E': 15}
    column_title = {'A': 'Name', 'B': 'T10', 'C': 'T8', 'D': 'Combined', 'E': 'Gold Rounded'}

    players = sorted(member, key=lambda player: player.t10 + player.t8, reverse=True)
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    for column, width in column_width.items():
        sheet.column_dimensions[column].width = width

    for column, title in column_title.items():
        sheet[f"{column}1"] = title

    sheet['J' + str(1)] = 'available Gold'
    sheet['J' + str(2)] = 0

    sheet['J' + str(4)] = 'calculated Gold to be payed out'
    sheet['J' + str(5)] = "=SUM(E2:E101)"

    sheet['J' + str(7)] = "Sum of all battles"
    sheet['J' + str(8)] = "=SUM(D2:D101)"

    sheet['J' + str(10)] = "Gold per battle"
    sheet['J' + str(11)] = "=J$2 / J$8"

    s = 2
    for player in players:
        sheet[f'A{s}'] = player.name
        sheet[f'B{s}'] = player.t10
        sheet[f'C{s}'] = player.t8
        sheet[f'D{s}'] = f"=B{s} + C{s}"
        sheet[f'E{s}'] = f"=ROUND(D{s}* J$11, 0)"
        s += 1

    sheet.column_dimensions.group('B', 'D', hidden=True)
    workbook.save(f'GoldClanTool-{"TEST"}-.xlsx')