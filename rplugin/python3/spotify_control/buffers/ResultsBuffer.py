from typing import Callable, List
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

    def handle_row_clicked_dropdown(self, row_nr: int, get_buffer_by_name: Callable[[str], Buffer]):
        row = self.get_data_row(row_nr)
        floating_options: List[str] = []
        if row.artists is not None:
            for artist in row.artists:
                floating_options.append(
                    f"Go to artist {artist.title}|{artist.uri}")
        if row.album is not None:
            floating_options.append(
                f"Go to album {row.album.title}|{row.album.uri}")
        formatted = ", ".join([f"'{opt}'" for opt in floating_options])
        self.vim.command(
            f"call spotify#open_floating([{formatted}], {self.number})")
