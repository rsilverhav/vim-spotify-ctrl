from spotify_control.buffer import Buffer

class UIHandler():
    def __init__(self, vim):
        self.vim = vim
        self.buffers = []

    def init_buffers(self, playlists):
        self.vim.command('tab new')
        # setting up results buffer with bindings
        results_buffer = Buffer("results", self.vim.current.buffer)
        self.buffers.append(results_buffer)
        self.vim.command('nmap <buffer> q :call SpotifyClose()<CR>')
        self.vim.command('nmap <buffer> f :call SpotifySearch()<CR>')
        self.vim.command('nmap <buffer> <Enter> :call SpotifyOpenResult({}, {})<CR>'.format(results_buffer.number, results_buffer.number))
        self.vim.command('vmap <buffer> <Enter> :call SpotifyPlayMultiple({}, {})<CR>'.format(results_buffer.number, results_buffer.number))

        # setting up playlist buffer with bindings
        self.vim.command('topleft vertical 32 new')
        playlist_buffer = Buffer("playlists", self.vim.current.buffer)
        playlist_buffer.set_data(playlists)
        self.buffers.append(playlist_buffer)
        self.vim.command('nmap <buffer> q :call SpotifyClose()<CR>')
        self.vim.command('nmap <buffer> f :call SpotifySearch()<CR>')
        self.vim.command('nmap <buffer> <Enter> :call SpotifyOpenResult({}, {})<CR>'.format(playlist_buffer.number, results_buffer.number))

        return self.buffers

    def close(self):
        for buffer in self.buffers:
            self.vim.command('bd {}'.format(buffer.number))

    def query_input(self, text):
        self.vim.command('let user_input = input("{}: ")'.format(text))
        return self.vim.eval('user_input')
