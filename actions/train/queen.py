"""Everything related to training queens goes here"""
from sc2.constants import LAIR, QUEEN


class TrainQueen:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main
        self.hatchery = None

    async def should_handle(self):
        """It possibly can get better but it seems good enough for now"""
        local_controller = self.controller
        self.hatchery = local_controller.townhalls.exclude_type(LAIR).noqueue.ready
        return (
            self.hatchery
            and len(local_controller.queens) < len(self.hatchery) + 1
            and not local_controller.already_pending(QUEEN)
            and local_controller.can_train(QUEEN, local_controller.pools.ready, False)
        )

    async def handle(self):
        """Execute the action of training queens"""
        self.controller.add_action(self.hatchery.random.train(QUEEN))
        return True
