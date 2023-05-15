from spotify_control.buffer import Buffer
from spotify_control.spotify import Spotify


class ResultsBuffer(Buffer):
    def __init__(self, vim, spotify: Spotify):
        super().__init__("results", vim, spotify)

    def format_line(self, data_item) -> str:
        return data_item["title"]

    def handle_row_clicked(self, row_nr: int, get_buffer_by_name):
        row_data = self.get_data_row(row_nr)
        self.vim.out_write(row_data['uri'])

    def refresh_buffer_data(self):
        return
