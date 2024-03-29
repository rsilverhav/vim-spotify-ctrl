from spotify_control.buffer import Buffer
from spotify_control.spotify import Spotify


class PlaylistsBuffer(Buffer):
    def __init__(self, vim, spotify: Spotify):
        super().__init__("playlists", vim, spotify)
        vim.command('set nonumber')

    def refresh_buffer_data(self):
        playlists = self.spotify.get_playlists()
        self.set_data(playlists)
