import logging

import pykka

from mopidy import backend
from mopidy_syncprojects.library import SyncprojectsLibraryProvider
from mopidy_syncprojects.syncprojects import SyncprojectsClient

logger = logging.getLogger(__name__)

SCHEMA = "sp"


class SyncprojectsBackend(pykka.ThreadingActor, backend.Backend):
    def __init__(self, config, audio):
        super().__init__()
        self.config = config
        self.remote = SyncprojectsClient(config)
        self.library = SyncprojectsLibraryProvider(backend=self)
        self.playback = SyncprojectsPlaybackProvider(audio=audio, backend=self)

        self.uri_schemes = ["syncprojects", SCHEMA]

    def on_start(self):
        username = self.remote.user.get("username")
        if username is not None:
            logger.info(f"Logged in to Syncprojects as {username!r}")


class SyncprojectsPlaybackProvider(backend.PlaybackProvider):
    def translate_uri(self, uri):
        track_id = self.backend.remote.get_uri_id(uri)
        track = self.backend.remote.get_track(track_id, True)
        if track is None:
            return None
        return track.uri
