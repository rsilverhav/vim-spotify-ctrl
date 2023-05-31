from spotify_control.buffer import Buffer
from spotify_control.spotify import Spotify


class QueueBuffer(Buffer):
    def __init__(self, vim, spotify: Spotify):
        super().__init__("queue", vim, spotify)
        vim.command('set nonumber')

    def refresh_buffer_data(self):
        respQueue = self.spotify.get_user_queue()
        respPrev = self.spotify.get_recently_played()

        tracks = respPrev
        if respQueue.current is not None:
            respQueue.current.title = "> " + respQueue.current.title
            tracks = tracks + [respQueue.current]
        tracks = tracks + respQueue.queue

        self.set_data(tracks)
        self.vim_buffer.clear_highlight(self.number)
        for i in range(0, len(respPrev)):
            self.vim_buffer.add_highlight("SpotifyPlayedSongs", i)
        self.vim_buffer.add_highlight("SpotifyCurrentlyPlaying", len(respPrev))
