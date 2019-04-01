"""Everything related to building logic for the hydralisk den goes here"""
from sc2.constants import UnitTypeId


class BuildHydraden:
    """Ok for now"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Requirement to build the hydraden"""
        return (
            self.main.can_build_unique(
                UnitTypeId.HYDRALISKDEN, self.main.hydradens, (self.main.lairs and self.main.pools)
            )
            and not self.main.close_enemy_production
            and not self.main.floating_buildings_bm
            and self.main.base_amount >= 3
        )

    async def handle(self):
        """Build the hydraden"""
        await self.main.place_building(UnitTypeId.HYDRALISKDEN)
