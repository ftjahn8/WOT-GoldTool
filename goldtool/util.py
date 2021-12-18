"""This file contains all Dataclasses and exceptions and the excel exporter function for this tool."""
import os

from typing import List
from datetime import datetime
from dataclasses import dataclass

import openpyxl


@dataclass
class ClanMember:
    """Represents a single clan member with account id and name and his battles in clan wars.
     at tier 8 and 10 for a single season."""
    name: str
    id: int
    season_id: str = None
    t8: int = 0
    t10: int = 0


@dataclass(frozen=True)
class Season:
    """Represents a single season on the globalmap (season or campaign!) with its id and name."""
    name: str
    id: str


class APIException(Exception):
    """Base Custom Exception for Exceptions occurring in the API communication."""


class InvalidAPIKeyException(APIException):
    """Special Exception for invalid API Key."""


class MissingResultException(APIException):
    """Special Exception for empty responses."""


def get_file_path(clan_tag: str, season: str) -> str:
    """
    Returns the path for the new file to export.
    Contains clan tag, season name and timestamp in the name.
    :param clan_tag: used clan tag
    :param season: used season
    :return: path of export file
    """
    now = datetime.now()
    timestamp = now.strftime("%d-%m-%Y_%H-%M")
    return f"{os.path.dirname(os.path.abspath(__file__))}{os.sep}GoldTool_{clan_tag}_{season}_{timestamp}.xlsx"


def export_to_excel(member: List[ClanMember], file_path: str) -> None:
    """
    Exports all data for the given clan members to an excel file.
    :param member: List of ClanMember objects containing all information to be exported
    :param file_path: target path to export file to
    :return: None
    """
    # format and titles of the hard coded excel structure
    column_width = {'A': 25, 'B': 10, 'C': 10, 'D': 10, 'E': 15}
    column_title = {'A': 'Name', 'B': 'T10', 'C': 'T8', 'D': 'Combined', 'E': 'Gold Rounded'}

    # sort players with most battles to the top
    players = sorted(member, key=lambda element: element.t10 + element.t8, reverse=True)

    # create new workbook and set default styling and titles
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    for column, width in column_width.items():
        sheet.column_dimensions[column].width = width

    for column, title in column_title.items():
        sheet[f"{column}1"] = title

    # set options on right side of prepared structure
    sheet['J' + str(1)] = 'available Gold'
    sheet['J' + str(2)] = 0

    sheet['J' + str(4)] = 'calculated Gold to be payed out'
    sheet['J' + str(5)] = "=SUM(E2:E101)"

    sheet['J' + str(7)] = "Sum of all battles"
    sheet['J' + str(8)] = "=SUM(D2:D101)"

    sheet['J' + str(10)] = "Gold per battle"
    sheet['J' + str(11)] = "=J$2 / J$8"

    # export all player data (name, number of battles) and set prepared functions to calculate deserved payouts
    current_row = 2
    for player in players:
        sheet[f'A{current_row}'] = player.name
        sheet[f'B{current_row}'] = player.t10
        sheet[f'C{current_row}'] = player.t8
        sheet[f'D{current_row}'] = f"=B{current_row} + C{current_row}"
        sheet[f'E{current_row}'] = f"=ROUND(D{current_row}* J$11, 0)"
        current_row += 1

    # hide battle counter columns
    sheet.column_dimensions.group('B', 'D', hidden=True)
    # save created excel file to hard drive
    workbook.save(file_path)
