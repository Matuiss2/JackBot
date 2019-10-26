import asyncio
import logging
import os.path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from typing import Any, List, Optional

import aiohttp
import portpicker

from sc2.versions import VERSIONS

from .controller import Controller
from .paths import Paths


LOGGER = logging.getLogger(__name__)


class KillSwitch:
    _to_kill: List[Any] = []

    @classmethod
    def add(cls, value):
        LOGGER.debug("kill_switch: Add switch")
        cls._to_kill.append(value)

    @classmethod
    def kill_all(cls):
        LOGGER.info("kill_switch: Process cleanup")
        for process in cls._to_kill:
            process._clean()


class SC2Process:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: Optional[int] = None,
        fullscreen: bool = False,
        render: bool = False,
        sc2_version: str = None,
    ) -> None:
        if not isinstance(host, str):
            raise AssertionError()
        if not (isinstance(port, int) or port is None):
            raise AssertionError()
        self._render = render
        self._fullscreen = fullscreen
        self._host = host
        if port is None:
            self._port = portpicker.pick_unused_port()
        else:
            self._port = port
        self._tmp_dir = tempfile.mkdtemp(prefix="SC2_")
        self._process = None
        self._session = None
        self._ws = None
        self._sc2_version = sc2_version

    async def __aenter__(self):
        KillSwitch.add(self)

        def signal_handler(*args):
            # unused arguments: signal handling library expects all signal
            # callback handlers to accept two positional arguments
            KillSwitch.kill_all()

        signal.signal(signal.SIGINT, signal_handler)

        try:
            self._process = self._launch()
            self._ws = await self._connect()
        except:
            await self._close_connection()
            self._clean()
            raise

        return Controller(self._ws, self)

    async def __aexit__(self, *args):
        KillSwitch.kill_all()
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    @property
    def ws_url(self):
        return f"ws://{self._host}:{self._port}/sc2api"

    @property
    def versions(self):
        """ Opens the versions.json file which origins from
        https://github.com/Blizzard/s2client-proto/blob/master/buildinfo/versions.json """
        return VERSIONS

    def find_data_hash(self, target_sc2_version: str):
        """ Returns the data hash from the matching version string. """
        for version in self.versions:
            if version["label"] == target_sc2_version:
                return version["data-hash"]
        return None

    def _launch(self):
        args = [
            str(Paths.EXECUTABLE),
            "-listen",
            self._host,
            "-port",
            str(self._port),
            "-displayMode",
            "1" if self._fullscreen else "0",
            "-dataDir",
            str(Paths.BASE),
            "-tempDir",
            self._tmp_dir,
        ]
        if self._sc2_version is not None:

            def special_match(strg: str, search=re.compile(r"([0-9]+\.[0-9]+?\.?[0-9]+)").search):
                """ Test if string contains only numbers and dots, which is a valid version string. """
                return not bool(search(strg))

            valid_version_string = special_match(self._sc2_version)
            if valid_version_string:
                data_hash = self.find_data_hash(self._sc2_version)
                if data_hash is None:
                    raise AssertionError(
                        f"StarCraft 2 Client version ({self._sc2_version}) was not found inside sc2/versions.py file."
                        f" Please check your spelling or check the versions.py file."
                    )
                args.extend(["-dataVersion", data_hash])
            else:
                LOGGER.warning(
                    f'The submitted version string in sc2.rungame() function call (sc2_version="{self._sc2_version}")'
                    f" does not match a normal version string. Running latest version instead."
                )

        if self._render:
            args.extend(["-eglpath", "libEGL.so"])

        if LOGGER.getEffectiveLevel() <= logging.DEBUG:
            args.append("-verbose")

        return subprocess.Popen(
            args,
            cwd=(str(Paths.CWD) if Paths.CWD else None),
            shell=True
            # , env=run_config.env
        )

    async def _connect(self):
        for i in range(60):
            if self._process is None:
                # The ._clean() was called, clearing the process
                LOGGER.debug("Process cleanup complete, exit")
                sys.exit()

            await asyncio.sleep(1)
            try:
                self._session = aiohttp.ClientSession()
                web_socket = await self._session.ws_connect(self.ws_url, timeout=120)
                LOGGER.debug("Websocket connection ready")
                return web_socket
            except aiohttp.client_exceptions.ClientConnectorError:
                await self._session.close()
                if i > 15:
                    LOGGER.debug("Connection refused (startup not complete (yet))")

        LOGGER.debug("Websocket connection to SC2 process timed out")
        raise TimeoutError("Websocket")

    async def _close_connection(self):
        LOGGER.info("Closing connection...")

        if self._ws is not None:
            await self._ws.close()

        if self._session is not None:
            await self._session.close()

    def _clean(self):
        LOGGER.info("Cleaning up...")

        if self._process is not None:
            if self._process.poll() is None:
                for _ in range(3):
                    self._process.terminate()
                    time.sleep(0.5)
                    if not self._process or self._process.poll() is not None:
                        break
                else:
                    self._process.kill()
                    self._process.wait()
                    LOGGER.error("KILLED")

        if os.path.exists(self._tmp_dir):
            shutil.rmtree(self._tmp_dir)

        self._process = None
        self._ws = None
        LOGGER.info("Cleanup complete")
