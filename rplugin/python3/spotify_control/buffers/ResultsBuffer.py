from spotify_control.buffer import Buffer
from spotify_control.spotify import Spotify


class ResultsBuffer(Buffer):
    def __init__(self, vim, spotify: Spotify):
        super().__init__("results", vim, spotify)

    def refresh_buffer_data(self):
        return

    def handle_rows_clicked(self, line_start: int, line_end: int, get_buffer_by_name):
        rows = self.get_data_rows(line_start, line_end)
        self.spotify.queue_songs(rows)
