"""Initialize the API"""
import sys
import logging
from pathlib import Path
from . import maps
from . import helpers
from .data import *
from .bot_ai import BotAI
from .main import run_game


def is_submodule(path):
    if path.is_file():
        return path.suffix == ".py" and path.stem != "__init__"
    if path.is_dir():
        return (path / "__init__.py").exists()
    return False


__all__ = [p.stem for p in Path(__file__).parent.iterdir() if is_submodule(p)]
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
LOGGER = logging.getLogger(__name__)
