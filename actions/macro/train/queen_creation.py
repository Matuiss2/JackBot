"""Everything related to training queens goes here"""
from sc2.constants import UnitTypeId


class QueenCreation:
    """It possibly can get better but it seems good enough for now"""

    def __init__(self, main):
        self.main = main
        self.hatcheries_and_hives = None

    async def should_handle(self):
        """Requirement for training the queens"""
        self.hatcheries_and_hives = self.main.townhalls.exclude_type(UnitTypeId.LAIR).idle.ready
        return (
            not self.main.close_enemies_to_base
            and self.hatcheries_and_hives
            and len(self.main.queens) <= self.main.ready_base_amount
            and not self.main.already_pending(UnitTypeId.QUEEN)
            and self.main.can_train(UnitTypeId.QUEEN, self.main.settled_pool, larva=False)
        )

    async def handle(self):
        """Execute the action of training queens"""
        self.main.add_action(self.hatcheries_and_hives.random.train(UnitTypeId.QUEEN))
