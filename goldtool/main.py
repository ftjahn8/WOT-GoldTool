"""import webbrowser
from threading import Thread

from kivy.app import App
from kivy.clock import mainthread
from kivy.config import Config
from kivy.properties import StringProperty


Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '400')
Config.set('graphics', 'resizable', '0')


class GoldTool(App):
    API_KEY = StringProperty()

    def on_start(self):
        self.lock_inputs()

    @staticmethod
    def open_dev_center():
        webbrowser.open("https://developers.wargaming.net/")

    def set_api_key(self, new_key: str) -> None:
        self.API_KEY = new_key
        if not new_key:
            self.set_warning("Missing API-Key!\nPlease enter an API-Key via the popup.")
            self.lock_inputs()
            self.root.ids.show_key.text = 'No Key entered.'
        else:
            self.set_warning("Please enter your clan tag and the season to evaluate.")
            self.lock_inputs(False)
            self.root.ids.show_key.text = new_key

    @mainthread
    def lock_inputs(self, value: bool = True):
        self.root.ids.clan_tag.disabled = value
        self.root.ids.create_button.disabled = value

    def update_season_select(self):
        pass

    def set_warning(self, text: str) -> None:
        self.root.ids.warning.text = text

    def start_procedure(self) -> None:
        api_key2 = self.root.ids.api_key.text
        clan_tag = self.root.ids.clan_tag.text

        if not api_key2:
            self.set_warning("Missing API-Key!\nPlease enter an API-Key via the popup.")
            return
        if not clan_tag:
            self.set_warning("Missing Clan-Tag!\nPlease enter a valid clan-tag.")
            return

        def procedure():
            clan_id = get_clan_id(api_key, clan_tag)
            clan_member = get_player_from_clan(api_key, clan_id)
            clan_member = get_season_battles(api_key, clan_member, "season_17")
            output(clan_member)
            self.lock_inputs(False)
            self.root.ids.api_key.disabled = False

        self.lock_inputs()
        self.root.ids.api_key.disabled = True
        Thread(target=procedure).start()


if __name__ == '__main__':
    GoldTool().run()"""
