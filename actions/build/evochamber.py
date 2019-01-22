"""Everything related to building logic for the evolution chamber goes here"""
from sc2.constants import EVOLUTIONCHAMBER


class BuildEvochamber:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Builds the evolution chambers"""
        local_controller = self.controller
        return (
            local_controller.building_requirement(EVOLUTIONCHAMBER, local_controller.pools.ready)
            and (
                len(local_controller.townhalls) >= 3
                or (local_controller.close_enemy_production and len(local_controller.spines.ready) >= 4)
            )
            and len(local_controller.evochambers) + local_controller.already_pending(EVOLUTIONCHAMBER) < 2
        )

    async def handle(self):
        """Build the evochamber"""
        build = await self.controller.place_building(EVOLUTIONCHAMBER)
        if not build:
            return False
        return True
