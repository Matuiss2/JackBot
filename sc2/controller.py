"""Group process requirements check and the creation of the game"""
from s2clientprotocol import sc2api_pb2 as sc_pb
from .protocol import Protocol
from .player import Computer


class Controller(Protocol):
    """It creates the game and checks processes"""

    def __init__(self, web_service, process):
        super().__init__(web_service)
        self._process = process

    @property
    def running(self):
        """Check if the process is running"""
        return self._process.process is not None

    async def create_game(self, game_map, players, realtime):
        """Create the game and show the log"""
        assert isinstance(realtime, bool)
        req = sc_pb.RequestCreateGame(local_map=sc_pb.LocalMap(map_path=str(game_map.relative_path)), realtime=realtime)
        for player in players:
            player_request = req.player_setup.add()
            player_request.type = player.type.value
            if isinstance(player, Computer):
                player_request.race = player.race.value
                player_request.difficulty = player.difficulty.value
        result = await self._execute(create_game=req)
        return result
