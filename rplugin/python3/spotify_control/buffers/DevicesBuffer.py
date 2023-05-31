from pynvim import Nvim
from spotify_control.buffer import Buffer
from spotify_control.spotify import Spotify


class DevicesBuffer(Buffer):
    def __init__(self, vim: Nvim, spotify: Spotify):
        super().__init__("devices", vim, spotify)

    def refresh_buffer_data(self):
        devices = self.spotify.get_devices()
        self.set_data(devices)

    def handle_row_clicked(self, row_nr: int, get_buffer_by_name):
        row = self.get_data_row(row_nr)
        if row.uri != "":
            self.spotify.make_uri_request(row.uri)
            self.refresh_buffer_data()
