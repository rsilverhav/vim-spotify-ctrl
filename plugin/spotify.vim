if !&rtp =~ 'plugin-name'
  if has('nvim')
    silent! UpdateRemotePlugins
  endif
endif

function! spotify#open_floating(items)
  let buf = nvim_create_buf(v:false, v:true)
  call nvim_buf_set_lines(buf, 0, -1, v:true, a:items)

  let str_length = 0
  for item in a:items
    let item_length = len(item)
    if item_length > str_length
      let str_length = item_length
    endif
  endfor

  let opts = {'relative': 'cursor', 'width': str_length, 'height': len(a:items), 'col': 0,
      \ 'row': 1, 'anchor': 'NW', 'style': 'minimal'}
  let win = nvim_open_win(buf, 0, opts)
  " optional: change highlight, otherwise Pmenu is used
  call nvim_win_set_option(win, 'winhl', 'Normal:MyHighlight')
  call win_gotoid(win)
endfunction

