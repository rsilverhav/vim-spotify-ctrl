if !&rtp =~ 'plugin-name'
  if has('nvim')
    silent! UpdateRemotePlugins
  endif
endif

function! spotify#open_floating(items, target_buffer)
  let buf = nvim_create_buf(v:false, v:true)

  let options = []
  let uris = []

  let str_length = 0
  for item in a:items
    let split_res = split(item, "|")
    let item_length = len(split_res[0])
    call add(uris, split_res[1])
    call add(options, split_res[0])
    if item_length > str_length
      let str_length = item_length
    endif
  endfor

  call nvim_buf_set_lines(buf, 0, -1, v:true, options)

  let opts = {'relative': 'cursor', 'width': str_length, 'height': len(a:items), 'col': 0,
      \ 'row': 1, 'anchor': 'NW', 'style': 'minimal', 'border': 'rounded'}
  let win = nvim_open_win(buf, 0, opts)
  " optional: change highlight, otherwise Pmenu is used
  call nvim_win_set_option(win, 'winhl', 'Normal:SpotifyGotoDropdown')
  call nvim_buf_set_option(buf, 'filetype', 'spotify_dropdown')
  call win_gotoid(win)

  let b:uris = uris
  let b:target_buffer = a:target_buffer

  return win
endfunction

function! spotify#choose_floating()
  let curr_line = line(".")
  call SpotifyOpenUri(b:target_buffer, b:uris[curr_line - 1])
  let target_buffer = b:target_buffer
  :q!
  execute "sb " . target_buffer
endfunction


hi SpotifyGotoDropdown ctermbg=6 ctermfg=1
autocmd BufLeave * if &ft == 'spotify_dropdown' | :q! | endif
autocmd Filetype spotify_dropdown nnoremap <buffer> <Esc> :q!<CR>
autocmd Filetype spotify_dropdown nnoremap <buffer> <Enter> :call spotify#choose_floating()<CR>
