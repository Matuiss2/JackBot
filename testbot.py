"""SC2 zerg bot by Helfull, Matuiss, Thommath and Tweakimp"""
import sc2
from sc2.constants import (SPAWNINGPOOL)
from actions.train.worker import TrainWorker
from actions.train.overlord import TrainOverlord
from actions.build.pool import BuildPool

# noinspection PyMissingConstructor
class EarlyAggro(sc2.BotAI):
    """It makes periodic attacks with good surrounding and targeting micro, it goes ultras end-game"""
    def __init__(self):
        self.commands = [
            TrainOverlord(self),
            TrainWorker(self),
            BuildPool(self)
        ]
        self.pools = []
        self.actions = []

    async def on_step(self, iteration):
        """Calls used units here, so it just calls it once per loop"""
        self.pools = self.units(SPAWNINGPOOL)
        self.actions = []

        for command in self.commands:
            if command.should_handle(iteration):
                print("Handling: {}".format(command.__class__))
                await command.handle(iteration)

        await self.do_actions(self.actions)
