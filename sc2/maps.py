"""Open maps and show its info"""
import logging
from .paths import Paths

LOGGER = logging.getLogger(__name__)


def get(name=None):
    """Returns a map"""
    maps = []
    for mapdir in (p for p in Paths.MAPS.iterdir()):
        if mapdir.is_dir():
            for mapfile in (p for p in mapdir.iterdir() if p.is_file()):
                if mapfile.suffix == ".SC2Map":
                    maps.append(Map(mapfile))
        elif mapdir.is_file():
            if mapdir.suffix == ".SC2Map":
                maps.append(Map(mapdir))
    if not name:
        return maps
    for selected_map in maps:
        if selected_map.matches(name):
            return selected_map
    raise KeyError(f"Map '{name}' was not found. Please put the map file in \"/StarCraft II/Maps/\".")


class Map:
    """Show map info(path, data, name) and ease its use"""

    def __init__(self, path):
        self.path = path
        if self.path.is_absolute():
            try:
                self.relative_path = self.path.relative_to(Paths.MAPS)
            except ValueError:  # path not relative to basedir
                logging.warning(f"Using absolute path: {self.path}")
                self.relative_path = self.path
        else:
            self.relative_path = self.path

    @property
    def name(self):
        """Return map name"""
        return self.path.stem

    @property
    def data(self):
        """Show map data"""
        with open(self.path, "rb") as file:
            return file.read()

    def matches(self, name):
        """Standardize the map names"""
        return self.name.lower().replace(" ", "") == name.lower().replace(" ", "")

    def __repr__(self):
        return f"Map({self.path})"
