from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable
from spotify_control.spotify import Spotify


class Buffer(ABC):
    def __init__(self, name, vim, spotify: Spotify):
        self.name = name
        self.vim_buffer = vim.current.buffer
        self.vim = vim
        self.spotify = spotify
        self.number = self.vim_buffer.number
        self.data = []
        self.vim_buffer.api.set_option('modifiable', False)
        self.vim_buffer.api.set_option('readonly', True)
        self.vim_buffer.api.set_option('bufhidden', 'hide')
        self.vim_buffer.api.set_option('buftype', 'nofile')
        self.vim_buffer.api.set_option('swapfile', False)
        self.vim_buffer.api.set_option('buflisted', False)
        self.vim_buffer.api.set_option('undolevels', -1)
        vim.command('nmap <silent> <buffer> q :call SpotifyClose()<CR>')
        vim.command('nmap <silent> <buffer> f :call SpotifySearch()<CR>')

        vim.command(
            f"nmap <silent> <buffer> <Enter> :call SpotifyHandleRowClicked({self.number})<CR>")

        self.vim.command(
            f"vmap <silent> <buffer> <Enter> :<c-u> call SpotifyHandleRowsClicked({self.number})<CR>")

        self.refresh_buffer_data()

    def format_line(self, data_item) -> str:
        return data_item["title"]

    def handle_row_clicked(self, row_nr: int, get_buffer_by_name: Callable[[str], Buffer]):
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
                self.vim.command(f'sb {result_buffer.number}')

    def handle_rows_clicked(self, row_start: int, row_end: int, get_buffer_by_name):
        pass

    @ abstractmethod
    def refresh_buffer_data(self):
        pass

    def set_data(self, data):
        self.data = list(data)
        lines = list(map(self.format_line, data))
        self.vim_buffer.api.set_option('modifiable', True)
        self.vim_buffer.api.set_option('readonly', False)

        self.vim_buffer.api.set_lines(0, -1, 0, lines)

        self.vim_buffer.api.set_option('modifiable', False)
        self.vim_buffer.api.set_option('readonly', True)

    def get_data_row(self, line_nr):
        index = line_nr - 1
        if index >= 0 and index < len(self.data):
            return self.data[index]

    def get_data_rows(self, line_start, line_end):
        index_start = line_start - 1
        if index_start >= 0 and line_end >= 0 and index_start < len(self.data) and line_end < len(self.data):
            return self.data[index_start:line_end]
