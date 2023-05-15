from spotify_control.buffers.ResultsBuffer import ResultsBuffer
from spotify_control.buffers.PlaylistsBuffer import PlaylistsBuffer
from spotify_control.buffer import Buffer
from spotify_control.spotify import Spotify


class UIHandler():
    def __init__(self, vim, spotify: Spotify):
        self.vim = vim
        self.spotify = spotify
        self.buffers = []

    def testFunc(self, buffer: Buffer):
        buffer.set_data([{"title": "WAT"}])

    def init_buffers(self):
        self.vim.command('tab new')
        # setting up results buffer with bindings
        results_buffer = ResultsBuffer(self.vim, self.spotify)
        self.buffers.append(results_buffer)

        # # self.vim.command(
        # #     f"nmap <buffer> <Enter> :call SpotifyOpenResult({results_buffer.number}, {results_buffer.number})<CR>")
        # self.vim.command(
        #    f"vmap <buffer> <Enter> :<c-u> call SpotifyQueueMultiple({results_buffer.number}, {results_buffer.number})<CR>")

        playlist_buffer = PlaylistsBuffer(self.vim, self.spotify)
        self.buffers.append(playlist_buffer)

        return self.buffers

    def close(self):
        for buffer in self.buffers:
            self.vim.command(f"bd {buffer.number}")

    def query_input(self, text):
        self.vim.command(f"let user_input = input('{text}: ')")
        return self.vim.eval('user_input')
