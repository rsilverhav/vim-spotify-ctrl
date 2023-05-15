from spotify_control.buffer import Buffer
from spotify_control.spotify import Spotify


class DevicesBuffer(Buffer):
    def __init__(self, vim, spotify: Spotify):
        super().__init__("devices", vim, spotify)

    def format_line(self, data_item) -> str:
        pre = "> " if data_item["is_active"] else ""
        return f"{pre}{data_item['title']} [vol: {data_item['volume_percent']}%]"

    def refresh_buffer_data(self):
        devices = self.spotify.get_devices()
        self.set_data(devices)

    def handle_row_clicked(self, row_nr: int, get_buffer_by_name):
        row = self.get_data_row(row_nr)
        if 'uri' in row:
            self.spotify.make_request(row["uri"])
            self.refresh_buffer_data()
