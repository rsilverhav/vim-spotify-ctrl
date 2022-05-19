import base64
import json
import requests
import urllib.request
from os.path import expanduser

home = expanduser("~")
TOKENS_FILE = home + "/.tokens.json"

class Spotify():
    def __init__(self, vim):
        self.vim = vim

    def get_auth_string(self):
        encode_str = self.vim.eval("g:spotify_client_id") + ":" + self.vim.eval("g:spotify_client_secret")
        print("encode_str = " + encode_str)
        encode = base64.b64encode(encode_str.encode())
        return "Basic " + encode.decode()

    def codeToToken(self):
        authorization = self.get_auth_string()

        resp = requests.post( url="https://accounts.spotify.com/api/token",
                headers={"Authorization": authorization},
                data={"grant_type": "authorization_code",
                    "code": CODE,
                    "redirect_uri": self.vim.eval("g:spotify_redirect_url")})
        print(resp)
        print(resp.content)

    def get_tokens(self):
        f = open(TOKENS_FILE, "r")
        tokens = json.loads(f.read())
        f.close()
        return tokens

    def refresh_token(self):
        tokens = self.get_tokens()
        resp = requests.post(url="https://accounts.spotify.com/api/token",
                data={"grant_type": "refresh_token", "refresh_token": self.vim.eval("g:spotify_refresh_token")},
                headers={"Authorization": self.get_auth_string()})
        new_tokens_string = resp.content.decode("utf-8")
        print(resp)
        print(new_tokens_string)
        f = open(TOKENS_FILE, "w")
        f.write(new_tokens_string)
        f.close()

    def make_spotify_request(self, url, method, params, retry_on_fail = True):
        tokens = self.get_tokens()
        resp = None
        if method == "POST":
            resp = requests.post(url=url, headers={"Authorization": "Bearer " + tokens["access_token"]}, data=params)
        elif method == "GET":
            resp = requests.get(url=url, headers={"Authorization": "Bearer " + tokens["access_token"]}, params=params)
        elif method == "PUT":
            resp = requests.put(url=url, headers={"Authorization": "Bearer " + tokens["access_token"], "Content-Type": "application/json"}, data=params)
        if resp.status_code == 200:
            content = json.loads(resp.content)
            return content
        elif resp.status_code == 204:
            return True
        elif retry_on_fail:
            self.refresh_token()
            return self.make_spotify_request(url, method, params, False)


    def get_my_info(self):
        tokens = self.get_tokens()
        resp = self.make_spotify_request("https://api.spotify.com/v1/me", "GET", {})
        print(resp)

    def get_playlists_data(self):
        tokens = self.get_tokens()
        resp = self.make_spotify_request("https://api.spotify.com/v1/me/playlists", "GET", {})
        return resp["items"]

    def get_playlists_tracks_data(self, playlist_id):
        tokens = self.get_tokens()
        url = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id)
        tracks_data = []
        while url != None:
            resp = self.make_spotify_request(url, "GET", {})
            tracks_data.extend(resp["items"])
            url = resp["next"]
        return tracks_data

    def play_track(self, track_id, context = None):
        track_uri = "spotify:track:{}".format(track_id)
        data = {}
        if context:
            data = { "context_uri": context, "offset": { "uri": track_uri }}
        else:
            data = { "uris": [track_uri] }
        resp = self.make_spotify_request("https://api.spotify.com/v1/me/player/play", "PUT", json.dumps(data))
        return resp

    def search(self, query):
        data = { 'q': query, 'type': 'album,artist,playlist,track' }
        resp = self.make_spotify_request("https://api.spotify.com/v1/search?{}", "GET", data)
        return resp

    def get_artist(self, id):
        url_top_tracks = 'https://api.spotify.com/v1/artists/{}/top-tracks'.format(id)
        top_tracks_data = self.make_spotify_request(url_top_tracks, "GET", { 'country': 'SE' })
        url_albums = 'https://api.spotify.com/v1/artists/{}/albums'.format(id)
        albums_data = self.make_spotify_request(url_albums, "GET", { 'country': 'SE' })
        return { "top_tracks": top_tracks_data, "albums": albums_data }

    def get_album_tracks(self, id):
        url = 'https://api.spotify.com/v1/albums/{}/tracks'.format(id)
        album_tracks = self.make_spotify_request(url, "GET", { 'limit': 50 })
        return album_tracks['items']


    def get_artists_names(self, data):
        return ', '.join(list(map(lambda artist: artist['name'], data)))

    def get_search_results(self, search_query):
        search_results_data = self.search(search_query)
        search_results = []
        search_results.append({ 'title': 'Tracks' })
        search_results.extend(self._parse_tracks_data(search_results_data['tracks']['items'], '  '))
        search_results.append({ 'title': 'Artists' })
        for artist in search_results_data['artists']['items']:
            search_results.append({ 'title': '  {}'.format(artist['name']), 'uri': artist['uri'] })
        search_results.append({ 'title': 'Albums' })
        search_results.extend(self._parse_albums_data(search_results_data['albums']['items'], '  '))
        return search_results

    def _parse_tracks_data(self, tracks_data, prefix = '', context = None):
        tracks = []
        for data in tracks_data:
            if 'track' in data:
                track_data = data['track']
            else:
                track_data = data
            artists = self.get_artists_names(track_data['artists'])
            title = '{} - {}'.format(track_data['name'], artists)
            parsed_track = { 'title': '{}{}'.format(prefix, title), 'uri': track_data['uri'] }
            if context:
                parsed_track['context'] = context
            tracks.append(parsed_track)
        return tracks

    def _parse_albums_data(self, albums_data, prefix = ''):
        albums = []
        for album in albums_data:
            title = '{}{}  by {}'.format(prefix, album['name'], self.get_artists_names(album['artists']))
            albums.append({ 'title': title, 'uri': album['uri'] })
        return albums

    def make_request(self, uri, context = None):
        id = uri.split(':')[-1]
        if 'playlist' in uri:
            tracks_data = self.get_playlists_tracks_data(id)
            tracks = self._parse_tracks_data(tracks_data, '', uri)
            return tracks
        elif 'track' in uri:
            self.play_track(id, context)
        elif 'artist' in uri:
            artist_data = self.get_artist(id)
            artist = [{'title': 'Tracks'}]
            artist.extend(self._parse_tracks_data(artist_data['top_tracks']['tracks'], '  '))
            artist.append({'title': 'Albums'})
            artist.extend(self._parse_albums_data(artist_data['albums']['items'], '  '))
            return artist
        elif 'album' in uri:
            album_tracks_data = self.get_album_tracks(id)
            album_tracks = self._parse_tracks_data(album_tracks_data, '', uri)
            return album_tracks
        return None
