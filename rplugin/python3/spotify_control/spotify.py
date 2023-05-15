import base64
import json
import requests
from os.path import expanduser

home = expanduser("~")
TOKENS_FILE = home + "/.tokens.json"
BASE_URL = "https://api.spotify.com/v1"


class Spotify():
    def __init__(self, client_id, client_secret, existing_refresh_token):
        self.client_id = client_id
        self.client_secret = client_secret
        self.spotify_refresh_token = existing_refresh_token

    def get_url(self, path: str):
        return f"{BASE_URL}{path}"

    def get_auth_string(self):
        encode_str = self.client_id + ":" + self.client_secret
        encode = base64.b64encode(encode_str.encode())
        return "Basic " + encode.decode()

    def get_tokens(self):
        f = open(TOKENS_FILE, "r", encoding="utf-8")
        tokens = json.loads(f.read())
        f.close()
        return tokens

    def refresh_token(self):
        resp = requests.post(url="https://accounts.spotify.com/api/token",
                             data={"grant_type": "refresh_token",
                                   "refresh_token": self.spotify_refresh_token},
                             headers={"Authorization": self.get_auth_string()}, timeout=60)
        new_tokens_string = resp.content.decode("utf-8")
        f = open(TOKENS_FILE, "w", encoding="utf-8")
        f.write(new_tokens_string)
        f.close()

    def make_spotify_request(self, url, method, params, retry_on_fail=True):
        tokens = self.get_tokens()
        resp = None
        if method == "POST":
            resp = requests.post(url=url, headers={
                                 "Authorization": "Bearer " + tokens["access_token"]}, data=params, timeout=60)
        elif method == "GET":
            resp = requests.get(url=url, headers={
                                "Authorization": "Bearer " + tokens["access_token"]}, params=params, timeout=60)
        elif method == "PUT":
            resp = requests.put(url=url, headers={
                                "Authorization": "Bearer " + tokens["access_token"], "Content-Type": "application/json"}, data=params, timeout=60)
        if resp.status_code == 200:
            content = json.loads(resp.content)
            return content
        elif resp.status_code == 204:
            return True
        elif retry_on_fail:
            self.refresh_token()
            return self.make_spotify_request(url, method, params, False)

    def make_all_pagination_request(self, url: str):
        all_items = []
        next_url = url
        while (next_url):
            resp = self.make_spotify_request(
                next_url, "GET", {})
            all_items += resp["items"]
            next_url = resp["next"]

        return all_items

    def get_my_info(self):
        return self.make_spotify_request(
            "/me", "GET", {})

    def get_playlists_data(self):
        playlists_data = self.make_all_pagination_request(
            self.get_url("/me/playlists"))
        return list(map(lambda playlist_data: {
            "title": playlist_data['name'], "uri": playlist_data['uri']}, playlists_data))

    def get_playlists_tracks_data(self, playlist_id):
        return self.make_all_pagination_request(self.get_url(f"/playlists/{playlist_id}/tracks"))

    def play_track(self, track_id, context=None):
        track_uri = f"spotify:track:{track_id}"
        data = {}
        if context:
            data = {"context_uri": context, "offset": {"uri": track_uri}}
        else:
            data = {"uris": [track_uri]}
        resp = self.make_spotify_request(
            self.get_url("/me/player/play"), "PUT", json.dumps(data))
        return resp

    def search(self, query):
        data = {'q': query, 'type': 'album,artist,playlist,track'}
        resp = self.make_spotify_request(
            self.get_url("/search?{}"), "GET", data)
        return resp

    def get_artist(self, id):
        url_top_tracks = self.get_url(f"/artists/{id}/top-tracks")
        top_tracks_data = self.make_spotify_request(
            url_top_tracks, "GET", {'country': 'SE'})
        url_albums = self.get_url(f"/artists/{id}/albums")
        albums_data = self.make_spotify_request(
            url_albums, "GET", {'country': 'SE'})
        return {"top_tracks": top_tracks_data, "albums": albums_data}

    def get_album_tracks(self, id):
        url = self.get_url(f"/albums/{id}/tracks")
        album_tracks = self.make_spotify_request(url, "GET", {'limit': 50})
        return album_tracks['items']

    def get_artists_names(self, data):
        return ', '.join(list(map(lambda artist: artist['name'], data)))

    def get_search_results(self, search_query):
        search_results_data = self.search(search_query)
        search_results = []
        search_results.append({'title': 'Tracks'})
        search_results.extend(self._parse_tracks_data(
            search_results_data['tracks']['items'], '  '))
        search_results.append({'title': 'Artists'})
        for artist in search_results_data['artists']['items']:
            search_results.append(
                {'title': f"  {artist['name']}", 'uri': artist['uri']})
        search_results.append({'title': 'Albums'})
        search_results.extend(self._parse_albums_data(
            search_results_data['albums']['items'], '  '))
        return search_results

    def queue_songs(self, songs_data):
        for song_data in songs_data:
            url_queue = self.get_url(
                f"/me/player/queue?uri={song_data['uri']}")
            self.make_spotify_request(url_queue, "POST", {})

    def _parse_tracks_data(self, tracks_data, prefix='', context=None):
        tracks = []
        for data in tracks_data:
            if 'track' in data:
                track_data = data['track']
            else:
                track_data = data
            artists = self.get_artists_names(track_data['artists'])
            title = f"{track_data['name']} - {artists}"
            parsed_track = {'title': f"{prefix}{title}",
                            'uri': track_data['uri']}
            if context:
                parsed_track['context'] = context
            tracks.append(parsed_track)
        return tracks

    def _parse_albums_data(self, albums_data, prefix=''):
        albums = []
        for album in albums_data:
            title = f"{prefix}{album['name']}  by {self.get_artists_names(album['artists'])}"
            albums.append({'title': title, 'uri': album['uri']})
        return albums

    def make_request(self, uri, context=None):
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
            artist.extend(self._parse_tracks_data(
                artist_data['top_tracks']['tracks'], '  '))
            artist.append({'title': 'Albums'})
            artist.extend(self._parse_albums_data(
                artist_data['albums']['items'], '  '))
            return artist
        elif 'album' in uri:
            album_tracks_data = self.get_album_tracks(id)
            album_tracks = self._parse_tracks_data(album_tracks_data, '', uri)
            return album_tracks
        return None

    def get_devices(self):
        devices = self.make_spotify_request(
            url=self.get_url("/me/player/devices"), method="GET", params={})
        return devices
