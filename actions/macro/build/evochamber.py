"""Everything related to building logic for the evolution chamber goes here"""
from sc2.constants import EVOLUTIONCHAMBER


class BuildEvochamber:
    """Can maybe be improved"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Requirements for building the evolution chambers, maybe its to early can probably be improved"""
        if (
            self.main.building_requirement(EVOLUTIONCHAMBER, self.main.pools.ready, one_at_time=True)
            and len(self.main.evochambers) < 2
        ):
            if not self.main.evochambers.ready:
                return self.main.base_amount >= 3
            return self.main.ready_base_amount >= 3

    async def handle(self):
        """Build the evochamber"""
        await self.main.place_building(EVOLUTIONCHAMBER)
        return True
