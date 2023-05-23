import pynvim
from spotify_control.spotify import Spotify
from spotify_control.ui_handler import UIHandler


@pynvim.plugin
class SpotifyControl(object):
    def __init__(self, vim):
        self.vim = vim
        self.buffers = []
        self.results_context = None
        self.spotify = None
        self.ui_handler = None

    def _get_buffer_by_name(self, name):
        for buffer in self.buffers:
            if buffer.name == name:
                return buffer
        return None

    def _get_buffer_by_number(self, number):
        for buffer in self.buffers:
            if buffer.number == number:
                return buffer
        return None

    @pynvim.command('SpotifyInit', range='', nargs='*', sync=True)
    def spotify_init(self, args, range):
        self.buffers = []
        spotify_client_id = self.vim.eval("g:spotify_client_id")
        spotify_client_secret = self.vim.eval("g:spotify_client_secret")
        spotify_refresh_token = self.vim.eval("g:spotify_refresh_token")
        self.spotify = Spotify(
            spotify_client_id, spotify_client_secret, spotify_refresh_token)
        self.ui_handler = UIHandler(self.vim, self.spotify)
        self.buffers = self.ui_handler.init_buffers()

    @pynvim.function('SpotifyHandleRowClicked')
    def function_handle_row_clicked(self, args):
        buf_nr = args[0]
        current_line = self.vim.eval('line(".")')
        self._get_buffer_by_number(buf_nr).handle_row_clicked(
            current_line, self._get_buffer_by_name)

    @pynvim.function('SpotifyHandleRowsClicked')
    def function_handle_rows_clicked(self, args):
        source_buf = args[0]
        [line_start] = self.vim.eval('getpos("\'<")[1:1]')
        [line_end] = self.vim.eval('getpos("\'>")[1:1]')
        self._get_buffer_by_number(
            source_buf).handle_rows_clicked(line_start, line_end, self._get_buffer_by_name)

    @pynvim.function('SpotifyRefreshBuffers')
    def function_refresh_buffers(self, args):
        for buffer in self.ui_handler.buffers:
            buffer.refresh_buffer_data()

    @pynvim.function('SpotifyClose')
    def function_close(self, args):
        self.ui_handler.close()

    @pynvim.function('SpotifySearch')
    def function_search(self, args):
        search_query = self.ui_handler.query_input('Spotify search')
        search_results = self.spotify.get_search_results(search_query)
        results_buffer = self._get_buffer_by_name('results')
        results_buffer.set_data(search_results)
        self.vim.command('set switchbuf=useopen')
        self.vim.command(f'sb {results_buffer.number}')
