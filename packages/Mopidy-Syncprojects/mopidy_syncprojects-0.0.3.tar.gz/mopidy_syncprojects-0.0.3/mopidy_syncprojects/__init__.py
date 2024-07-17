import pathlib

import pkg_resources

from mopidy import config, ext
from mopidy.exceptions import ExtensionError

__version__ = pkg_resources.get_distribution("Mopidy-Syncprojects").version


class Extension(ext.Extension):

    dist_name = "Mopidy-Syncprojects"
    ext_name = "syncprojects"
    version = __version__

    def get_default_config(self):
        return config.read(pathlib.Path(__file__).parent / "ext.conf")

    def get_config_schema(self):
        schema = super().get_config_schema()
        schema["auth_token"] = config.Secret()
        return schema

    def validate_config(self, config):  # no_coverage
        if not config.getboolean("syncprojects", "enabled"):
            return
        if not config.get("syncprojects", "auth_token"):
            raise ExtensionError(
                "In order to use the Syncprojects extension, you must provide "
                "an auth token. For more information refer to "
                "https://github.com/k3an3/mopidy-syncprojects/"
            )

    def setup(self, registry):
        from .actor import SyncprojectsBackend

        registry.add("backend", SyncprojectsBackend)
