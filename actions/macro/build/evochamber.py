"""Everything related to building logic for the evolution chamber goes here"""
from sc2.constants import EVOLUTIONCHAMBER


class BuildEvochamber:
    """Can maybe be improved"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Requirements for building the evolution chambers, maybe its to early can probably be improved"""
        return (
            self.controller.building_requirement(EVOLUTIONCHAMBER, self.controller.pools.ready)
            and (
                self.controller.base_amount >= 3
                or (self.controller.close_enemy_production and len(self.controller.spines.ready) >= 4)
            )
            and len(self.controller.evochambers) + self.controller.already_pending(EVOLUTIONCHAMBER) < 2
        )

    async def handle(self):
        """Build the evochamber"""
        build = await self.controller.place_building(EVOLUTIONCHAMBER)
        if not build:
            return False
        return True
