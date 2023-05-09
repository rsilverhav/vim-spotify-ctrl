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
        self.ui_handler = UIHandler(self.vim)
        playlists_data = self.spotify.get_playlists_data()
        playlists = list(map(lambda playlist_data: {
                         "title": playlist_data['name'], "uri": playlist_data['uri']}, playlists_data))
        self.buffers = self.ui_handler.init_buffers(playlists)

    @pynvim.function('SpotifyOpenResult')
    def function_open_result(self, args):
        source_buf = args[0]
        target_buf = args[1]
        current_line = self.vim.eval('line(".")')
        row = self._get_buffer_by_number(source_buf).get_data_row(current_line)
        if 'uri' in row:
            context = None
            if 'context' in row:
                context = row['context']
            new_data = self.spotify.make_request(row['uri'], context)
            if new_data:
                self._get_buffer_by_number(target_buf).set_data(new_data)
                self.vim.command('set switchbuf=useopen')
                self.vim.command('sb {}'.format(target_buf))

    @pynvim.function('SpotifyQueueMultiple')
    def function_queue_multiple(self, args):
        source_buf = args[0]
        [line_start] = self.vim.eval('getpos("\'<")[1:1]')
        [line_end] = self.vim.eval('getpos("\'>")[1:1]')
        rows = self._get_buffer_by_number(
            source_buf).get_data_rows(line_start, line_end)
        self.spotify.queue_songs(rows)

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
        self.vim.command('sb {}'.format(results_buffer.number))
