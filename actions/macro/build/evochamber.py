"""Everything related to building logic for the evolution chamber goes here"""
from sc2.constants import EVOLUTIONCHAMBER


class BuildEvochamber:
    """Can maybe be improved"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Requirements for building the evolution chambers, maybe its to early can probably be improved"""
        return (
            self.main.building_requirement(EVOLUTIONCHAMBER, self.main.pools.ready)
            and (self.main.base_amount >= 3 or (self.main.close_enemy_production and len(self.main.spines.ready) >= 4))
            and len(self.main.evochambers.ready) + self.main.already_pending(EVOLUTIONCHAMBER) < 2
        )

    async def handle(self):
        """Build the evochamber"""
        await self.main.place_building(EVOLUTIONCHAMBER)
        return True
