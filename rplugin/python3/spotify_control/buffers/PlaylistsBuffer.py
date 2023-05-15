from spotify_control.buffer import Buffer
from spotify_control.spotify import Spotify


class PlaylistsBuffer(Buffer):
    def __init__(self, vim, spotify: Spotify):
        vim.command('topleft vertical 32 new')
        super().__init__("playlists", vim, spotify)
        vim.command('set nonumber')

    def format_line(self, data_item) -> str:
        return data_item["title"]

    def handle_row_clicked(self, row_nr: int, get_buffer_by_name):
        result_buffer = get_buffer_by_name('results')
        row = self.get_data_row(row_nr)
        if result_buffer and 'uri' in row:
            context = None
            if 'context' in row:
                context = row['context']
            new_data = self.spotify.make_request(row['uri'], context)
            if new_data:
                result_buffer.set_data(new_data)
                self.vim.command('set switchbuf=useopen')
                self.vim.command('sb {}'.format(result_buffer.number))

    def refresh_buffer_data(self):
        playlists = self.spotify.get_playlists_data()
        self.set_data(playlists)
