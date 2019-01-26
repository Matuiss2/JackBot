"""Everything related to building logic for the hydralisk den goes here"""
from sc2.constants import HYDRALISKDEN


class BuildHydraden:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main
        self.selected_pools = None

    async def should_handle(self):
        """Requirement to build the hydraden"""
        local_controller = self.controller
        self.selected_pools = local_controller.pools
        return (
            local_controller.can_build_unique(
                HYDRALISKDEN, local_controller.hydradens, (local_controller.lairs and self.selected_pools)
            )
            and not local_controller.close_enemy_production
            and not local_controller.floating_buildings_bm
            and len(local_controller.townhalls) >= 3
        )

    async def handle(self):
        """Build the hydraden"""
        build = await self.controller.place_building(HYDRALISKDEN)
        if not build:
            return False
        return True
