# Spotify ctrl

Plugin for neovim used to control the playback and browse Spotify.

## Getting started

### Getting access token from Spotify
1. Visit `https://developer.spotify.com/dashboard/applications` and create an app
2. Add a Redirect URI to `http://localhost:3000/`
3. Start a simple webserver, for example `node express`, on port 3000
4. Go to `https://accounts.spotify.com/authorize?response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2F&client_id=<Client id>`, remember to insert your Client id for your Spotify app in the url. This url will redirect you to the specified redirect_uri with the query param `code` set in the url, copy it
7. Get your AUTH by running `python3 -c 'import base64;print(base64.b64encode("<Client ID>:<Client Secret>".encode()).decode("utf-8"))`
6. Run the following curl to get the refresh token: `curl --request POST -H "Authorization: Basic <AUTH>" -H "Content-type: application/x-www-form-urlencoded" -d "grant_type=authorization_code" -d "code=<code from previous step>" -d "redirect_uri=http://localhost:3000/" https://accounts.spotify.com/api/token`
7. Copy the `refresh_token` in the response and setup vim to set the following variables:
```
let g:spotify_client_id = "<Client ID>"
let g:spotify_client_secret = "<Client Secret>"
let g:spotify_refresh_token = "<refresh token from step 7>"
```
