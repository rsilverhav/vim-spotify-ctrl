import pynvim
from spotify_control.spotify import Spotify
from spotify_control.ui_handler import UIHandler


@pynvim.plugin
class SpotifyControl(object):
    def __init__(self, vim: pynvim.Nvim):
        self.vim = vim
        self.buffers = []
        self.results_context = None
        self.spotify = None
        self.ui_handler = None

    def _get_buffer_by_name(self, name: str):
        for buffer in self.buffers:
            if buffer.name == name:
                return buffer
        return None

    def _get_buffer_by_number(self, number):
        for buffer in self.buffers:
            if buffer.number == number:
                return buffer
        return None

    def _get_current_line(self):
        current_line = self.vim.eval('line(".")')
        if not isinstance(current_line, dict) and not isinstance(current_line, list):
            return int(current_line)
        else:
            return 0

    @pynvim.command('SpotifyInit', range='', nargs=0, sync=True)
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
        current_line = self._get_current_line()
        buffer = self._get_buffer_by_number(buf_nr)
        if buffer is not None:
            buffer.handle_row_clicked(
                current_line, self._get_buffer_by_name)

    @pynvim.function('SpotifyHandleRowsClicked')
    def function_handle_rows_clicked(self, args):
        source_buf = args[0]
        [line_start] = self.vim.eval('getpos("\'<")[1:1]')
        [line_end] = self.vim.eval('getpos("\'>")[1:1]')
        buffer = self._get_buffer_by_number(
            source_buf)
        if buffer is not None:
            buffer.handle_rows_clicked(
                line_start, line_end, self._get_buffer_by_name)

    @pynvim.function('SpotifyHandleRowClickedShift')
    def function_handle_row_clicked_shift(self, args):
        buf_nr = args[0]
        current_line = self._get_current_line()
        buffer = self._get_buffer_by_number(
            buf_nr)
        if buffer is not None:
            buffer.handle_row_clicked_dropdown(
                current_line, self._get_buffer_by_name)

    @pynvim.function('SpotifyRefreshBuffers')
    def function_refresh_buffers(self, args):
        if self.ui_handler is not None:
            for buffer in self.ui_handler.buffers:
                buffer.refresh_buffer_data()
        else:
            self.vim.out_write("Call init before trying to refresh buffers")

    @pynvim.function('SpotifyOpenUri')
    def function_open_uri(self, args):
        target_buffer = args[0]
        uri = args[1]
        if self.spotify is not None:
            buffer = self._get_buffer_by_number(target_buffer)
            if buffer is not None:
                resp = self.spotify.make_uri_request(uri)
                buffer.set_data(resp)
            else:
                self.vim.out_write(
                    "Failed to find target buffer when opening URI")
        else:
            self.vim.out_write("Init Spotify client before trying to open URI")

    @pynvim.function('SpotifyClose')
    def function_close(self, args):
        if self.ui_handler is not None:
            self.ui_handler.close()

    @pynvim.function('SpotifySearch')
    def function_search(self, args):
        if self.ui_handler is not None and self.spotify is not None:
            search_query = self.ui_handler.query_input('Spotify search')
            if len(search_query) == 0:
                return

            search_results = self.spotify.get_search_results(search_query)
            results_buffer = self._get_buffer_by_name('results')
            if results_buffer is not None:
                results_buffer.set_data(search_results)
                self.vim.command('set switchbuf=useopen')
                self.vim.command(f'sb {results_buffer.number}')
            else:
                self.vim.out_write("Failed to search, result buffer not found")
