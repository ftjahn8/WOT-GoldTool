"""This file contains the application class for the Gold Tool."""
import webbrowser
from threading import Thread
from requests import HTTPError

from kivy.app import App
from kivy.clock import mainthread
from kivy.config import Config
from kivy.properties import StringProperty

from goldtool.api import get_season, get_clan_id, get_player_from_clan, get_season_battles
from goldtool.util import export_to_excel, InvalidAPIKeyException, APIException, MissingResultException, get_file_path

# Update kivy settings
Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '400')
Config.set('graphics', 'resizable', '0')
Config.set('input', 'mouse', 'mouse, multitouch_on_demand')


class GoldTool(App):
    """Main Application class for this Tool."""

    API_KEY = StringProperty()
    '''entered API-Key for the complete process.'''

    season_lookup = {}
    '''Lookup Season name -> Season ID'''

    def on_start(self):
        self.lock_inputs()

    @mainthread
    def lock_inputs(self, value: bool = True) -> None:
        """
        Locks or unlocks all Buttons and Inputs for the main analysis process.
        :param value: if True locks else unlocks
        :return: None
        """
        self.root.ids.clan_tag.disabled = value
        self.root.ids.season.disabled = value
        self.root.ids.create_button.disabled = value

    @mainthread
    def reset(self) -> None:
        """
        Reset Inputs after a successful export process.
        :return: None
        """
        self.root.ids.season.text = "No Season selected"
        self.root.ids.clan_tag.text = ""

    @mainthread
    def set_warning(self, text: str) -> None:
        """
        Sets text in the warning box.
        :param text: Text to be shown in the warning box.
        :return: None
        """
        self.root.ids.warning.text = text

    @staticmethod
    def open_dev_center() -> None:
        """
        Opens the dev wargaming center in a browser.
        :return: None
        """
        webbrowser.open("https://developers.wargaming.net/")

    def set_api_key(self, new_key: str) -> None:
        """
        Sets the api key and updates the input and show fields.
        :param new_key: entered API key to be saved
        :return: None
        """
        self.API_KEY = new_key
        if not new_key:
            self.set_warning("Missing API-Key!\nPlease enter an API-Key via the popup.")
            self.lock_inputs()
            self.root.ids.show_key.text = 'No Key entered.'
        else:
            self.set_warning("Please enter a clan tag and select the season to evaluate.")
            self.lock_inputs(False)
            self.root.ids.show_key.text = new_key
            self.update_season_select()

    def update_season_select(self) -> None:
        """
        Sets the options to select in the season dropdown.
        :return: None
        """
        try:
            seasons = get_season(self.API_KEY)
        except InvalidAPIKeyException:
            self.set_warning("Your API-Key is invalid. Please correct it.")
        else:
            # set season lookup to solve name -> id later.
            self.season_lookup = {season.name: season.id for season in seasons}
            self.root.ids.season.values = list(self.season_lookup.keys())

    def start_procedure(self) -> None:
        """
        Starts to import the inputs, checks for validation and starts the big analysis process
        :return:
        """
        season = self.root.ids.season.text
        clan_tag = self.root.ids.clan_tag.text

        # check inputs beeing not empty
        if not clan_tag:
            self.set_warning("Missing Clan-Tag!\nPlease enter a valid Clan-Tag.")
            return

        if season == "No Season selected":
            self.set_warning("Missing Season!\nPlease select a season in the dropdown.")
            return

        # lookup id to season name
        season_id = self.season_lookup[season]

        def analysis_procedure():
            """main procedure to create output, separated by gui through thread to prevent gui from freezing"""
            try:
                clan_id = get_clan_id(self.API_KEY, clan_tag)
                clan_member = get_player_from_clan(self.API_KEY, clan_id)
                clan_member = get_season_battles(self.API_KEY, clan_member, season_id)
            except InvalidAPIKeyException:
                self.set_warning("Your API-Key is invalid. Please correct it."
                                 "\nCurrent Process was cancelled therefore.")
            except MissingResultException:
                self.set_warning("Your Clan Tag was not found! Please correct it."
                                 "\nCurrent Process was cancelled therefore.")
            except (APIException, HTTPError) as unexpected_exc:
                self.set_warning(f"Unexpected Error. Stopped process due to error:"
                                 f"\n{type(unexpected_exc)}: {str(unexpected_exc.value)}")
            else:
                # eeeeeeeeeeeeeeeeeeeexport!
                file_path = get_file_path(clan_tag, season)
                export_to_excel(clan_member, file_path)
                self.set_warning(f"Exported Results successfully to {file_path}.\nYou can now start another process.")
                self.reset()
            self.lock_inputs(False)
            self.root.ids.api_key.disabled = False

        # look input and inform user about start of process
        self.lock_inputs()
        self.root.ids.api_key.disabled = True
        self.set_warning("Started Analysis...\nPlease wait a moment. (Process can take up to two minutes.)")
        # start as a thread to stop freezing guis.
        Thread(target=analysis_procedure).start()


if __name__ == '__main__':
    GoldTool().run()
