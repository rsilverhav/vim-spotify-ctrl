import json

class Buffer():
    def __init__(self, name, vim_buffer):
        self.name = name
        self.vim_buffer = vim_buffer
        self.number = vim_buffer.number
        self.data = []
        self.vim_buffer.api.set_option('modifiable', False)
        self.vim_buffer.api.set_option('readonly', True)
        self.vim_buffer.api.set_option('bufhidden', 'hide')
        self.vim_buffer.api.set_option('buftype', 'nofile')
        self.vim_buffer.api.set_option('swapfile', False)
        self.vim_buffer.api.set_option('buflisted', False)
        self.vim_buffer.api.set_option('undolevels', -1)

    def set_data(self, data):
        self.data = list(data)
        lines = list(map(lambda data_item: data_item['title'], data))
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
