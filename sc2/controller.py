import logging
from s2clientprotocol import sc2api_pb2 as sc_pb
from .protocol import Protocol
from .player import Computer


LOGGER = logging.getLogger(__name__)


class Controller(Protocol):
    def __init__(self, ws, process):
        super().__init__(ws)
        self.__process = process

    @property
    def running(self):
        return self.__process._process is not None

    async def create_game(self, game_map, players, realtime):
        assert isinstance(realtime, bool)
        req = sc_pb.RequestCreateGame(local_map=sc_pb.LocalMap(map_path=str(game_map.relative_path)), realtime=realtime)

        for player in players:
            player_setup = req.player_setup.add()
            player_setup.type = player.type.value
            if isinstance(player, Computer):
                player_setup.race = player.race.value
                player_setup.difficulty = player.difficulty.value

        LOGGER.info("Creating new game")
        LOGGER.info(f"Map:     {game_map.name}")
        LOGGER.info(f"Players: {', '.join(str(p) for p in players)}")
        result = await self._execute(create_game=req)
        return result
