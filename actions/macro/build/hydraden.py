"""Everything related to building logic for the hydralisk den goes here"""
from sc2.constants import HYDRALISKDEN


class BuildHydraden:
    """Ok for now"""

    def __init__(self, main):
        self.main = main
        self.selected_pools = None

    async def should_handle(self):
        """Requirement to build the hydraden"""
        self.selected_pools = self.main.pools
        return (
            self.main.can_build_unique(HYDRALISKDEN, self.main.hydradens, (self.main.lairs and self.selected_pools))
            and not self.main.close_enemy_production
            and not self.main.floating_buildings_bm
            and self.main.base_amount >= 3
        )

    async def handle(self):
        """Build the hydraden"""
        build = await self.main.place_building(HYDRALISKDEN)
        if not build:
            return False
        return True
