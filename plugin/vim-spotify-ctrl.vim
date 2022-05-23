if !&rtp =~ 'plugin-name'
  if has('nvim')
    silent! UpdateRemotePlugins
  endif
endif
