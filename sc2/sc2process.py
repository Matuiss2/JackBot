"""Groups everything related to the processes"""
from typing import Any, Optional, List
import logging
import sys
import signal
import time
import asyncio
import os.path
import shutil
import tempfile
import subprocess
import portpicker
import aiohttp
from .paths import Paths
from .controller import Controller

LOGGER = logging.getLogger(__name__)


class KillSwitch:
    """Add processes to the kill list and kill then"""

    _to_kill: List[Any] = []

    @classmethod
    def add(cls, value):
        """Add process to kill"""
        LOGGER.debug("kill_switch: Add switch")
        cls._to_kill.append(value)

    @classmethod
    def kill_all(cls):
        """Kill all processes"""
        LOGGER.info("kill_switch: Process cleanup")
        for process in cls._to_kill:
            process.clean()


class SC2Process:
    """Kill, clean, opens and connects the processes"""

    def __init__(self, host: str = "127.0.0.1", port: Optional[int] = None, fullscreen: bool = False) -> None:
        assert isinstance(host, str)
        assert isinstance(port, int) or port is None

        self._fullscreen = fullscreen
        self._host = host
        if port is None:
            self._port = portpicker.pick_unused_port()
        else:
            self._port = port
        self._tmp_dir = tempfile.mkdtemp(prefix="SC2_")
        self.process = None
        self._session = None
        self._ws = None

    async def __aenter__(self):
        KillSwitch.add(self)

        def signal_handler():
            KillSwitch.kill_all()

        signal.signal(signal.SIGINT, signal_handler)

        try:
            self.process = self._launch()
            self._ws = await self._connect()
        except:
            await self._close_connection()
            self.clean()
            raise

        return Controller(self._ws, self)

    async def __aexit__(self, *args):
        KillSwitch.kill_all()
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    @property
    def ws_url(self):
        """Get the argument url"""
        return f"ws://{self._host}:{self._port}/sc2api"

    def _launch(self):
        """Launch the exe"""
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
        if LOGGER.getEffectiveLevel() <= logging.DEBUG:
            args.append("-verbose")
        return subprocess.Popen(args, cwd=(str(Paths.CWD) if Paths.CWD else None))

    async def _connect(self):
        """Performs the connection to the server"""
        for i in range(60):
            if not self.process:
                sys.exit()
            await asyncio.sleep(1)
            try:
                self._session = aiohttp.ClientSession()
                ws = await self._session.ws_connect(self.ws_url, timeout=60)
                return ws
            except aiohttp.client_exceptions.ClientConnectorError:
                await self._session.close()
                if i > 15:
                    LOGGER.debug("Connection refused (startup not complete (yet))")

        LOGGER.debug("Websocket connection to SC2 process timed out")
        raise TimeoutError("Websocket")

    async def _close_connection(self):
        """Closes the connection to the server"""
        if self._ws is not None:
            await self._ws.close()
        if self._session is not None:
            await self._session.close()

    def clean(self):
        """Cleaning the remaining processes"""
        if self.process is not None:
            if self.process.poll() is None:
                for _ in range(3):
                    self.process.terminate()
                    time.sleep(0.5)
                    if self.process.poll() is not None:
                        break
                else:
                    self.process.kill()
                    self.process.wait()
                    LOGGER.error("KILLED")
        if os.path.exists(self._tmp_dir):
            shutil.rmtree(self._tmp_dir)
        self.process = None
        self._ws = None
