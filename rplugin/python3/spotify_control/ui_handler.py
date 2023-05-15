from spotify_control.buffers.DevicesBuffer import DevicesBuffer
from spotify_control.buffers.ResultsBuffer import ResultsBuffer
from spotify_control.buffers.PlaylistsBuffer import PlaylistsBuffer
from spotify_control.buffer import Buffer
from spotify_control.spotify import Spotify


class UIHandler():
    def __init__(self, vim, spotify: Spotify):
        self.vim = vim
        self.spotify = spotify
        self.buffers: list[Buffer] = []

    def init_buffers(self):
        self.vim.command('tab new')

        results_buffer = ResultsBuffer(self.vim, self.spotify)
        self.buffers.append(results_buffer)

        self.vim.command('botright horizontal 6 new')
        devices_buffer = DevicesBuffer(self.vim, self.spotify)
        self.buffers.append(devices_buffer)

        self.vim.command('topleft vertical 48 new')
        playlist_buffer = PlaylistsBuffer(self.vim, self.spotify)
        self.buffers.append(playlist_buffer)

        return self.buffers

    def close(self):
        for buffer in self.buffers:
            self.vim.command(f"bd {buffer.number}")

    def query_input(self, text):
        self.vim.command(f"let user_input = input('{text}: ')")
        return self.vim.eval('user_input')
