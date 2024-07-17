import datetime
import logging
import re
import string
from contextlib import closing
from urllib.parse import quote_plus

import requests
import time
import unicodedata
from mopidy import httpclient
from mopidy.models import Album, Artist, Track
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError

import mopidy_syncprojects

logger = logging.getLogger(__name__)


def safe_url(uri):
    return quote_plus(
        unicodedata.normalize("NFKD", uri).encode("ASCII", "ignore")
    )


def readable_url(uri):
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    safe_uri = (
        unicodedata.normalize("NFKD", uri).encode("ascii", "ignore").decode()
    )
    return re.sub(
        r"\s+", " ", "".join(c for c in safe_uri if c in valid_chars)
    ).strip()


def get_user_url(user_id):
    return "me" if not user_id else f"users/self/"


def get_requests_session(proxy_config, user_agent, token, public=False):
    proxy = httpclient.format_proxy(proxy_config)
    full_user_agent = httpclient.format_user_agent(user_agent)

    session = requests.Session()
    session.proxies.update({"http": proxy, "https": proxy})
    if not public:
        session.headers.update({"user-agent": full_user_agent})
        session.headers.update({"Authorization": f"Token {token}"})

    return session


def get_mopidy_requests_session(config, public=False):
    return get_requests_session(
        proxy_config=config["proxy"],
        user_agent=(
            f"{mopidy_syncprojects.Extension.dist_name}/"
            f"{mopidy_syncprojects.__version__}"
        ),
        token=config["syncprojects"]["auth_token"],
        public=public,
    )


class cache:  # noqa
    # TODO: merge this to util library

    def __init__(self, ctl=8, ttl=3600):
        self.cache = {}
        self.ctl = ctl
        self.ttl = ttl
        self._call_count = 1

    def __call__(self, func):
        def _memoized(*args):
            self.func = func
            now = time.time()
            try:
                value, last_update = self.cache[args]
                age = now - last_update
                if self._call_count >= self.ctl or age > self.ttl:
                    self._call_count = 1
                    raise AttributeError

                self._call_count += 1
                return value

            except (KeyError, AttributeError):
                value = self.func(*args)
                self.cache[args] = (value, now)
                return value

            except TypeError:
                return self.func(*args)

        return _memoized


class ThrottlingHttpAdapter(HTTPAdapter):
    def __init__(self, burst_length, burst_window, wait_window):
        super().__init__()
        self.max_hits = burst_length
        self.hits = 0
        self.rate = burst_length / burst_window
        self.burst_window = datetime.timedelta(seconds=burst_window)
        self.total_window = datetime.timedelta(
            seconds=burst_window + wait_window
        )
        self.timestamp = datetime.datetime.min

    def _is_too_many_requests(self):
        now = datetime.datetime.utcnow()
        if now < self.timestamp + self.total_window:
            elapsed = now - self.timestamp
            self.hits += 1
            if (now < self.timestamp + self.burst_window) and (
                    self.hits < self.max_hits
            ):
                return False
            else:
                logger.debug(
                    f"Request throttling after {self.hits} hits in "
                    f"{elapsed.microseconds} us "
                    f"(window until {self.timestamp + self.total_window})"
                )
                return True
        else:
            self.timestamp = now
            self.hits = 0
            return False

    def send(self, request, **kwargs):
        if request.method == "HEAD" and self._is_too_many_requests():
            resp = requests.Response()
            resp.request = request
            resp.url = request.url
            resp.status_code = 429
            resp.reason = (
                "Client throttled to {self.rate:.1f} requests per second"
            )
            return resp
        else:
            return super().send(request, **kwargs)


def sanitize_list(tracks):
    return [t for t in tracks if t]


class SyncprojectsClient:
    public_client_id = None

    def __init__(self, config):
        super().__init__()
        self.explore_songs = config["syncprojects"].get("explore_songs", 25)
        self.http_client = get_mopidy_requests_session(config)
        adapter = ThrottlingHttpAdapter(
            burst_length=3, burst_window=1, wait_window=10
        )
        self.http_client.mount("https://www.syncprojects.app/", adapter)

        self.public_stream_client = get_mopidy_requests_session(
            config, public=True
        )

    @property
    @cache()
    def user(self):
        return self._get("users/self/")

    @cache(ttl=10)
    def get_projects(self):
        projects = self._get('projects/', multi=True)
        return self.parse_projects(projects)

    @cache(ttl=10)
    def get_songs(self, artist_id=None):
        if artist_id:
            projects = [self._get(f'projects/{artist_id}/')]
        else:
            projects = self._get('projects/', multi=True)
        return self.parse_songs_from_projects(projects)

    @cache()
    def get_track_artwork(self, track_id):
        track = self._get(f"songs/{track_id}/")
        if track["album"] is not None:
            album = self.get_album(track["album"])
            if album["cover"] is not None:
                return album["cover"]
        artist = self.get_project(track["project"])
        return artist["image"]

    @cache()
    def get_track(self, track_id, streamable=False):
        logger.debug(f"Getting info for track with ID {track_id}")
        try:
            return self.parse_track(self._get(f"songs/{track_id}/"), None, streamable)
        except Exception:
            import traceback
            traceback.print_exc()
            return None

    @cache()
    def get_project(self, project_id):
        logger.debug(f"Getting info for project with ID {project_id}")
        try:
            return self._get(f"projects/{project_id}/")
        except Exception:
            return None

    @cache()
    def get_album(self, album_id):
        logger.debug(f"Getting info for album with ID {album_id}")
        try:
            return self._get(f"albums/{album_id}/")
        except Exception:
            return None

    @staticmethod
    def get_uri_id(track):
        logger.debug(f"Parsing track {track}")
        if hasattr(track, "uri"):
            track = track.uri
        return track.split(".")[-1]

    def search(self, query):
        raise NotImplementedError()
        query = quote_plus(query.encode("utf-8"))
        search_results = self._get(f"tracks?q={query}", limit=True)
        tracks = []
        for track in search_results:
            tracks.append(self.parse_track(track))
        return sanitize_list(tracks)

    def parse_songs_from_projects(self, res):
        tracks = []
        logger.debug(f"Parsing {len(res)} result(s)...")
        for project in res:
            for song in project['songs']:
                tracks.append(self.parse_track(song, project))
        return sanitize_list(tracks)

    def parse_projects(self, res):
        artists = []
        logger.debug(f"Parsing {len(res)} result(s)...")
        for project in res:
            artists.append(self.parse_artists(project))
        return sanitize_list(artists)

    def _get(self, path, limit=None, multi=False):
        url = f"https://www.syncprojects.app/api/v1/{path}"
        params = []
        if limit:
            params.insert(0, ("limit", self.explore_songs))
        try:
            if multi:
                results = []
            while True:
                with closing(self.http_client.get(url, params=params)) as res:
                    logger.debug(f"Requested {res.url}")
                    res.raise_for_status()
                    j = res.json()
                    if not multi:
                        return j
                    results.extend(j['results'])
                    if 'next' in j and j['next'] is not None:
                        url = j['next']
                    else:
                        return results
        except Exception as e:
            if isinstance(e, HTTPError) and e.response.status_code == 401:
                logger.error(
                    'Invalid "auth_token" used for Syncprojects '
                    "authentication!"
                )
            else:
                logger.error(f"Syncprojects API request failed: {e}")
        return {}

    @cache()
    def parse_artists(self, project):
        artist_kwargs = {"name": project["name"],
                         "uri": f"syncprojects:artist/{readable_url(project['name'])}.{project['id']}"}

        return Artist(**artist_kwargs)

    @cache()
    def parse_track(self, song, project=None, remote_url=False):
        if song['url'] is None:
            return None
        if project is None:
            project = self.get_project(song['project'])

        if song['album'] is not None:
            album = self.get_album(song['album'])
        else:
            album = {'name': "Unknown Album"}

        track_kwargs = {}
        artist_kwargs = {}
        album_kwargs = {}

        track_kwargs["name"] = song["name"]
        track_kwargs["length"] = song["duration"] * 1000
        if song["album_order"] is not None:
            track_kwargs["track_no"] = song["album_order"]
        artist_kwargs["name"] = project["name"]
        album_kwargs["name"] = album["name"]

        if remote_url:
            track_kwargs["uri"] = song["url"]
        else:
            track_kwargs[
                "uri"
            ] = f"syncprojects:song/{readable_url(song['name'])}.{song['id']}"

        if artist_kwargs:
            track_kwargs["artists"] = [Artist(**artist_kwargs)]

        if album_kwargs:
            track_kwargs["album"] = Album(**album_kwargs)

        return Track(**track_kwargs)

    @staticmethod
    def parse_fail_reason(reason):
        return "" if reason == "Unknown" else f"({reason})"
