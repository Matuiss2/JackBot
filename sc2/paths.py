"""Group the path for sc2.exe on all OS"""
import os
from pathlib import Path
import platform
import re
import logging

LOGGER = logging.getLogger(__name__)

BASEDIR = {
    "Windows": "C:/Program Files (x86)/StarCraft II",
    "Darwin": "/Applications/StarCraft II",
    "Linux": "~/StarCraftII",
}

USERPATH = {
    "Windows": r"\Documents\StarCraft II\ExecuteInfo.txt",
    "Darwin": r"/Library/Application Support/Blizzard/StarCraft II/ExecuteInfo.txt",
}

BINPATH = {"Windows": "SC2_x64.exe", "Darwin": "SC2.app/Contents/MacOS/SC2", "Linux": "SC2_x64"}

CWD = {"Windows": "Support64", "Darwin": None, "Linux": None}

PF = platform.system()


def latest_executable(versions_dir):
    """Return the path for the sc2.exe"""
    latest = max((int(p.name[4:]), p) for p in versions_dir.iterdir() if p.is_dir() and p.name.startswith("Base"))
    version, path = latest
    if version < 55958:
        LOGGER.critical(f"Your SC2 binary is too old. Upgrade to 3.16.1 or newer.")
        exit(1)
    return path / BINPATH[PF]


class _MetaPaths(type):
    """"Lazily loads paths to allow importing the library even if SC2 isn't installed."""

    def __setup(cls):
        if PF not in BASEDIR:
            LOGGER.critical(f"Unsupported platform '{PF}'")
            exit(1)

        try:
            base = os.environ.get("SC2PATH")
            if base is None and USERPATH[PF] is not None:
                einfo = str(Path.home().expanduser()) + USERPATH[PF]
                if os.path.isfile(einfo):
                    with open(einfo) as file:
                        content = file.read()
                    if content:
                        base = re.search(r" = (.*)Versions", content).group(1)
                        if not os.path.exists(base):
                            base = None
            if base is None:
                base = BASEDIR[PF]
            cls.BASE = Path(base).expanduser()
            cls.EXECUTABLE = latest_executable(cls.BASE / "Versions")
            cls.CWD = cls.BASE / CWD[PF] if CWD[PF] else None

            cls.REPLAYS = cls.BASE / "Replays"

            if (cls.BASE / "maps").exists():
                cls.MAPS = cls.BASE / "maps"
            else:
                cls.MAPS = cls.BASE / "Maps"
        except FileNotFoundError as error:
            LOGGER.critical(f"SC2 installation not found: File '{error.filename}' does not exist.")
            exit(1)

    def __getattr__(cls, attr):
        cls.__setup()
        return getattr(cls, attr)


class Paths(metaclass=_MetaPaths):
    """Paths for SC2 folders, lazily loaded using the above metaclass."""
