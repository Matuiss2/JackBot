"""Everything related to training queens goes here"""
from sc2.constants import LAIR, QUEEN


class TrainQueen:
    """It possibly can get better but it seems good enough for now"""

    def __init__(self, main):
        self.controller = main
        self.hatchery = None

    async def should_handle(self):
        """Requirement for training the queens"""
        self.hatchery = self.controller.townhalls.exclude_type(LAIR).noqueue.ready
        return (
            self.hatchery
            and len(self.controller.queens) <= self.controller.base_amount
            and not self.controller.already_pending(QUEEN)
            and self.controller.can_train(QUEEN, self.controller.pools.ready, larva=False)
        )

    async def handle(self):
        """Execute the action of training queens"""
        self.controller.add_action(self.hatchery.random.train(QUEEN))
        return True
