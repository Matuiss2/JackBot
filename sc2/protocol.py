import aiohttp

import logging

LOGGER = logging.getLogger(__name__)

from s2clientprotocol import sc2api_pb2 as sc_pb

from .data import Status
from .player import Computer


class ProtocolError(Exception):
    pass


class ConnectionAlreadyClosed(ProtocolError):
    pass


class Protocol(object):
    def __init__(self, ws):
        assert ws
        self._ws = ws
        self._status = None

    async def __request(self, request):
        LOGGER.debug(f"Sending request: {request !r}")
        try:
            await self._ws.send_bytes(request.SerializeToString())
        except TypeError:
            LOGGER.exception("Cannot send: Connection already closed.")
            raise ConnectionAlreadyClosed("Connection already closed.")
        LOGGER.debug(f"Request sent")

        response = sc_pb.Response()
        try:
            response_bytes = await self._ws.receive_bytes()
        except TypeError:
            LOGGER.exception("Cannot receive: Connection already closed.")
            raise ConnectionAlreadyClosed("Connection already closed.")
        response.ParseFromString(response_bytes)
        LOGGER.debug(f"Response received")
        return response

    async def _execute(self, **kwargs):
        assert len(kwargs) == 1, "Only one request allowed"

        request = sc_pb.Request(**kwargs)

        response = await self.__request(request)

        new_status = Status(response.status)
        if new_status != self._status:
            LOGGER.info(f"Client status changed to {new_status} (was {self._status})")
        self._status = new_status

        if response.error:
            LOGGER.debug(f"Response contained an error: {response.error}")
            raise ProtocolError(f"{response.error}")

        return response

    async def ping(self):
        result = await self._execute(ping=sc_pb.RequestPing())
        return result

    async def quit(self):
        await self._execute(quit=sc_pb.RequestQuit())
