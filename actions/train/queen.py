"""Everything related to training queens goes here"""
from sc2.constants import LAIR, QUEEN


class TrainQueen:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai
        self.hatchery = None
        self.hatcheries_random = None

    async def should_handle(self, iteration):
        """It possibly can get better but it seems good enough for now"""

        self.hatchery = self.ai.townhalls.exclude_type(LAIR).noqueue.ready
        if self.hatchery:
            self.hatcheries_random = self.hatchery.random

        return (
            self.hatchery
            and self.ai.pools.ready
            and len(self.ai.queens) < len(self.hatchery) + 1
            and not self.ai.already_pending(QUEEN)
            and self.ai.can_train(QUEEN, larva=False)
        )

    async def handle(self, iteration):
        """Execute the action of training queens"""
        self.ai.add_action(self.hatcheries_random.train(QUEEN))
        return True
