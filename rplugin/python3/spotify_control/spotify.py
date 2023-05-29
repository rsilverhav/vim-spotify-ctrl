import base64
import json
import requests
from os.path import expanduser
from collections import namedtuple
from typing import List

home = expanduser("~")
TOKENS_FILE = home + "/.tokens.json"
BASE_URL = "https://api.spotify.com/v1"

UserQueue = namedtuple("UserQueue", ["current", "queue"])
Player = namedtuple(
    "Player", ["context_title", "context_uri", "current_item_title"])


# class Context():
#     formatted_title: str
#     uri: str
#
#     def __init__(self, formatted_title: str, uri: str):
#         self.formatted_title = formatted_title
#         self.uri = uri
#
#
# class Artist():
#     formatted_title: str
#     uri: str
#
#     def __init__(self,
#                  formatted_title: str,
#                  uri: str
#                  ):
#
#         self.formatted_title = formatted_title
#         self.uri = uri


class SpotifyNode:
    title: str
    uri: str

    def __init__(self,
                 title: str,
                 uri: str
                 ):

        self.title = title
        self.uri = uri


class ResponseRow:
    title: str
    uri: str
    context: SpotifyNode | None
    artists: List[SpotifyNode] | None
    album: SpotifyNode | None

    def __init__(self, title: str, uri: str, context: SpotifyNode | None = None,
                 artists: List[SpotifyNode] | None = None, album: SpotifyNode | None = None):
        self.title = title
        self.uri = uri
        self.context = context
        self.artists = artists
        self.album = album


# class Track():
#     formatted_title: str
#     artists: List[Artist]
#     name: str
#     uri: str
#     context: str
#
#     def __init__(self,
#                  artists: List[Artist],
#                  name: str,
#                  uri: str,
#                  context: str | None = None):
#         self.formatted_title = f"{name} - {artists}"
#         self.artists = artists
#         self.name = name
#         self.uri = uri
#         self.context = context
#
#
# class Playlist():
#     name: str
#     uri: str
#     tracks: List[Track]
#
#     def __init__(self,
#                  name: str,
#                  uri: str,
#                  tracks: List[Track]
#                  ):
#         self.name = name
#         self.uri = uri
#         self.tracks = tracks


class Spotify():
    def __init__(self, client_id, client_secret, existing_refresh_token, print_debug=False):
        self.client_id = client_id
        self.client_secret = client_secret
        self.spotify_refresh_token = existing_refresh_token
        self.print_debug = print_debug

    def _get_url(self, path: str):
        return f"{BASE_URL}{path}"

    def _get_auth_string(self):
        encode_str = self.client_id + ":" + self.client_secret
        encode = base64.b64encode(encode_str.encode())
        return "Basic " + encode.decode()

    def _get_tokens(self):
        f = open(TOKENS_FILE, "r", encoding="utf-8")
        tokens = json.loads(f.read())
        f.close()
        return tokens

    def _refresh_token(self):
        resp = requests.post(url="https://accounts.spotify.com/api/token",
                             data={"grant_type": "refresh_token",
                                   "refresh_token": self.spotify_refresh_token},
                             headers={"Authorization": self._get_auth_string()}, timeout=60)
        new_tokens_string = resp.content.decode("utf-8")
        f = open(TOKENS_FILE, "w", encoding="utf-8")
        f.write(new_tokens_string)
        f.close()

    def _make_spotify_request(self, url, method, params={}, retry_on_fail=True):
        tokens = self._get_tokens()
        resp = None
        if self.print_debug:
            print(f"[{method}] {url}, params: {params}")

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
            self._refresh_token()
            return self._make_spotify_request(url, method, params, False)

    def _make_all_pagination_request(self, url: str):
        all_items = []
        next_url = url
        while (next_url):
            resp = self._make_spotify_request(
                next_url, "GET", {})
            all_items += resp["items"]
            next_url = resp["next"]

        return all_items

    def _parse_tracks_data(self, tracks_data, prefix='', context=None) -> List[ResponseRow]:
        tracks: List[ResponseRow] = []
        for data in tracks_data:
            if 'track' in data:
                track_data = data['track']
            else:
                track_data = data
            artists = self._parse_artists(track_data['artists'])
            artist_names = ", ".join([art.title for art in artists])
            title = f"{track_data['name']} - {artist_names}"
            parsed_track = ResponseRow(f"{prefix}{title}", track_data['uri'], artists=artists)
            if context:
                parsed_track.context = context
            tracks.append(parsed_track)
        return tracks

    def _get_artists_names(self, artists):
        return ", ".join([artist["name"] for artist in artists])

    def _parse_albums_data(self, albums_data, prefix='') -> List[ResponseRow]:
        return [ResponseRow(f"{prefix}{album['name']}  by {self._get_artists_names(album['artists'])}", album['uri']) for album in albums_data]

    def _parse_playlists_result_data(self, playlists_data, prefix='') -> List[ResponseRow]:
        return [ResponseRow(f"{prefix}{playlist['name']}", playlist['uri']) for playlist in playlists_data]

    def get_playlists(self) -> List[ResponseRow]:
        playlists_data = self._make_all_pagination_request(
            self._get_url("/me/playlists"))
        return [ResponseRow(playlist_data['name'], playlist_data['uri']) for playlist_data in playlists_data]

    def play_track(self, track_id, context=None):
        track_uri = f"spotify:track:{track_id}"
        data = {}
        if context:
            data = {"context_uri": context, "offset": {"uri": track_uri}}
        else:
            data = {"uris": [track_uri]}
        resp = self._make_spotify_request(
            self._get_url("/me/player/play"), "PUT", json.dumps(data))
        return resp

    def _get_artist(self, artist_id):
        url_top_tracks = self._get_url(f"/artists/{artist_id}/top-tracks")
        top_tracks_data = self._make_spotify_request(
            url_top_tracks, "GET", {'country': 'SE'})
        url_albums = self._get_url(f"/artists/{artist_id}/albums")
        albums_data = self._make_spotify_request(
            url_albums, "GET", {'country': 'SE'})
        return {"top_tracks": top_tracks_data, "albums": albums_data}

    def _get_album_tracks(self, track_id):
        url = self._get_url(f"/albums/{track_id}/tracks")
        album_tracks = self._make_spotify_request(url, "GET", {'limit': 50})
        return album_tracks['items']

    def _parse_artists(self, data) -> List[ResponseRow]:
        return [ResponseRow(artist['name'], artist['uri']) for artist in data]

    def get_search_results(self, search_query) -> List[ResponseRow]:
        data = {'q': search_query, 'type': 'album,artist,playlist,track'}
        search_results_data = self._make_spotify_request(
            self._get_url("/search?{}"), "GET", data)
        search_results: List[ResponseRow] = []
        result_spacing = '  '
        search_results.append(ResponseRow('Tracks', ''))
        search_results.extend(self._parse_tracks_data(
            search_results_data['tracks']['items'], result_spacing))
        search_results.append(ResponseRow('Artists', ''))
        for artist in search_results_data['artists']['items']:
            search_results.append(
                ResponseRow(f"  {artist['name']}", artist['uri']))
        search_results.append(ResponseRow('Albums', ''))
        search_results.extend(self._parse_albums_data(
            search_results_data['albums']['items'], result_spacing))
        search_results.append(ResponseRow('Playlists', ''))
        search_results.extend(self._parse_playlists_result_data(
            search_results_data['playlists']['items'], result_spacing))
        return search_results

    def queue_songs(self, songs_data):
        for song_data in songs_data:
            url_queue = self._get_url(
                f"/me/player/queue?uri={song_data['uri']}")
            self._make_spotify_request(url_queue, "POST", {})

    def change_device(self, device_id: str):
        self._make_spotify_request(self._get_url(
            "/me/player"), method="PUT", params=json.dumps(
            {'device_ids': [device_id], 'play': True}
        ))

    def make_uri_request(self, uri, context=None):
        if uri == '':
            return None
        uri_id = uri.split(':')[-1]
        if 'playlist' in uri:
            tracks_data = self._make_all_pagination_request(
                self._get_url(f"/playlists/{uri_id}/tracks"))
            tracks = self._parse_tracks_data(tracks_data, '', uri)
            return tracks
        elif 'track' in uri:
            self.play_track(uri_id, context)
        elif 'artist' in uri:
            artist_data = self._get_artist(uri_id)
            artist = [{'title': 'Tracks'}]
            artist.extend(self._parse_tracks_data(
                artist_data['top_tracks']['tracks'], '  '))
            artist.append({'title': 'Albums'})
            artist.extend(self._parse_albums_data(
                artist_data['albums']['items'], '  '))
            return artist
        elif 'album' in uri:
            album_tracks_data = self._get_album_tracks(uri_id)
            album_tracks = self._parse_tracks_data(album_tracks_data, '', uri)
            return album_tracks
        elif 'device' in uri:
            self.change_device(uri_id)
            return None
        return None

    def get_devices(self):
        resp = self._make_spotify_request(
            url=self._get_url("/me/player/devices"), method="GET")
        return [{"title": device["name"], "uri": f"spotify:device:{device['id']}", "is_active": device['is_active'], "volume_percent": device['volume_percent']} for device in resp["devices"]]

    def get_user_queue(self) -> UserQueue:
        resp = self._make_spotify_request(
            url=self._get_url("/me/player/queue"), method="GET")
        currently_playing = resp["currently_playing"]
        if currently_playing is not None:
            current = self._parse_tracks_data([currently_playing])[0]
        else:
            current = None
        queue = self._parse_tracks_data([item for item in resp["queue"]])
        return UserQueue(current, queue)

    def get_recently_played(self):
        resp = self._make_spotify_request(url=self._get_url(
            "/me/player/recently-played"), method="GET")
        items = self._parse_tracks_data([i["track"] for i in resp["items"]])
        items.reverse()
        return items

    def get_player(self) -> Player:
        resp = self._make_spotify_request(
            url=self._get_url("/me/player"), method="GET")
        # context_info = self.make_uri_request(resp['context']['uri'])
        player = Player(resp["context"]["uri"], resp["context"]["uri"],
                        self._parse_tracks_data([resp['item']])[0]['title'])
        return player
