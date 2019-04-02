"""Everything related to training queens goes here"""
from sc2.constants import UnitTypeId


class TrainQueen:
    """It possibly can get better but it seems good enough for now"""

    def __init__(self, main):
        self.main = main
        self.hatchery = None

    async def should_handle(self):
        """Requirement for training the queens"""
        self.hatchery = self.main.townhalls.exclude_type(UnitTypeId.LAIR).idle.ready
        return (
            not self.main.close_enemies_to_base
            and self.hatchery
            and len(self.main.queens) <= self.main.ready_base_amount
            and not self.main.already_pending(UnitTypeId.QUEEN)
            and self.main.can_train(UnitTypeId.QUEEN, self.main.pools.ready, larva=False)
        )

    async def handle(self):
        """Execute the action of training queens"""
        self.main.add_action(self.hatchery.random.train(UnitTypeId.QUEEN))
