import collections
import logging
import re
import urllib.parse

from mopidy import backend, models
from mopidy.models import SearchResult, Track, Image

from mopidy_syncprojects.syncprojects import SyncprojectsClient

logger = logging.getLogger(__name__)


def generate_uri(path):
    return f"syncprojects:directory:{urllib.parse.quote('/'.join(path))}"


def new_folder(name, path):
    return models.Ref.directory(uri=generate_uri(path), name=name)


def simplify_search_query(query):
    if isinstance(query, dict):
        r = []
        for v in query.values():
            if isinstance(v, list):
                r.extend(v)
            else:
                r.append(v)
        return " ".join(r)
    if isinstance(query, list):
        return " ".join(query)
    else:
        return query


class SyncprojectsLibraryProvider(backend.LibraryProvider):
    root_directory = models.Ref.directory(
        uri="syncprojects:directory", name="Syncprojects"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vfs = {"syncprojects:directory": {}}
        self.add_to_vfs(new_folder("Artists", ["artist"]))
        self.add_to_vfs(new_folder("Songs", ["song"]))

    def add_to_vfs(self, _model):
        self.vfs["syncprojects:directory"][_model.uri] = _model

    def tracklist_to_vfs(self, track_list):
        vfs_list = collections.OrderedDict()
        for temp_track in track_list:
            if not isinstance(temp_track, Track):
                temp_track = self.backend.remote.parse_track(temp_track)
            if hasattr(temp_track, "uri"):
                vfs_list[temp_track.name] = models.Ref.track(
                    uri=temp_track.uri, name=temp_track.name
                )
        return list(vfs_list.values())

    def browse(self, uri):
        logger.info("Called browse(%s)", uri)
        if not self.vfs.get(uri):
            req_type, res_id = re.match(r".*:(\w*)(?:/(.*))?", uri).groups()
            if res_id:
                res_id = SyncprojectsClient.get_uri_id(res_id)
            if req_type == "song" or req_type == "artist" and res_id is not None:
                return self.tracklist_to_vfs(
                    self.backend.remote.get_songs(res_id)
                )
            elif req_type == "artist":
                artists = self.backend.remote.get_projects()
                for a in artists:
                    new_folder(a.name, ["artist", a.uri])
                return [models.Ref.artist(uri=a.uri, name=a.name) for a in artists]
            else:
                logger.error("Requested unknown URI type %s", req_type)
        # root directory
        return list(self.vfs.get(uri, {}).values())

    def get_images(self, uris):
        results = {}
        logger.info("req images: %s", uris)
        for uri in uris:
            req_type, res_id = re.match(r".*:(\w*)(?:/(.*))?", uri).groups()
            res_id = SyncprojectsClient.get_uri_id(res_id)
            if req_type == "song":
                image = self.backend.remote.get_track_artwork(res_id)
                if image:
                    results[uri] = [Image(uri=image)]
            else:
                logger.error("Requested unsupported URI type %s", req_type)
        return results

    def search(self, query=None, uris=None, exact=False):
        raise NotImplementedError()

    def lookup(self, uri):
        try:
            track_id = self.backend.remote.get_uri_id(uri)
            track = self.backend.remote.get_track(track_id)
            if track is None:
                logger.info(
                    f"Failed to lookup {uri}: Syncprojects track not found"
                )
                return []
            return [track]
        except Exception as error:
            logger.error(f"Failed to lookup {uri}: {error}")
            return []
