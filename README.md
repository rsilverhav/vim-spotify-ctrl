# vim-spotify-ctrl

Plugin for neovim used to control the playback and browse Spotify.

## Version note
This plugin is in early alpha and may not work as intended on all systems and information might be missing in setup. Configurability is limited.

## Getting started

### Getting access token from Spotify
1. Visit `https://developer.spotify.com/dashboard/applications` and create an app
2. Add a Redirect URI to `http://localhost:3000/`
3. Start a simple webserver, for example `node express`, on port 3000
4. Go to `https://accounts.spotify.com/authorize?response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2F&client_id=<Client id>`, remember to insert your Client id for your Spotify app in the url. This url will redirect you to the specified redirect_uri with the query param `code` set in the url, copy it
7. Get your AUTH by running `python3 -c 'import base64;print(base64.b64encode("<Client ID>:<Client Secret>".encode()).decode("utf-8"))`
6. Run the following curl to get the refresh token: `curl --request POST -H "Authorization: Basic <AUTH>" -H "Content-type: application/x-www-form-urlencoded" -d "grant_type=authorization_code" -d "code=<code from previous step>" -d "redirect_uri=http://localhost:3000/" https://accounts.spotify.com/api/token`
7. Warning: The following information should NOT be commited to git as this is private info. Copy the `refresh_token` in the response and setup vim to set the following variables:
```
let g:spotify_client_id = "<Client ID>"
let g:spotify_client_secret = "<Client Secret>"
let g:spotify_refresh_token = "<refresh token from step 7>"
```

### Install dependencies
`requests` for Python3 is required to run the plugin, to install it run:
```
pip3 install requests
```


## Usage
To start the plugin call the function `SpotifyInit`. Example binding: `nnoremap <Leader>s :SpotifyInit<CR>`.

Use `<Enter>` to interact with rows in buffers.

To search, use `f` in one of the buffers opened by the plugin. The search result will open in the `results` buffer.

Interacting with a single row in the `results` buffer will either open that resource (album or artist) or play the selected song. Interacting with song rows in visual mode in the `results` buffer will queue the selected songs.

Using the binding `gd` in the `results` or `queue` buffer will open a "goto" dropdown showing different options based on the data for the row.

Interacting with a single row in the `playlists` buffer will open the playlist in the `results` buffer.

Interacting with a single row in the `devices` will change which device to play music from. The active device is prefixed with `>  `.

The `queue` buffer shows previously played songs (only songs played from start to finish), current song with green text and queued songs.

The plugin will not reload any content automatically, to reload the current buffers content use `r` in any buffers opened by the plugin.

To close all buffers opened by the plugin use `q` in any plugin buffer.
