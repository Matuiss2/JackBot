"""Everything related to building logic for the hydralisk den goes here"""
from sc2.constants import HYDRALISKDEN


class BuildHydraden:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main
        self.selected_pools = None

    async def should_handle(self):
        """Requirement to build the hydraden"""
        self.selected_pools = self.controller.pools
        return (
                self.controller.can_build_unique(
                HYDRALISKDEN, self.controller.hydradens, (self.controller.lairs and self.selected_pools)
            )
            and not self.controller.close_enemy_production
            and not self.controller.floating_buildings_bm
            and len(self.controller.townhalls) >= 3
        )

    async def handle(self):
        """Build the hydraden"""
        build = await self.controller.place_building(HYDRALISKDEN)
        if not build:
            return False
        return True
