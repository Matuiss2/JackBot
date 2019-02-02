"""Everything related to building logic for the pools goes here"""
from sc2.constants import SPAWNINGPOOL


class BuildPool:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Requirement for building the spawning pool"""
        local_controller = self.controller
        return local_controller.can_build_unique(SPAWNINGPOOL, local_controller.pools) and (
            len(local_controller.townhalls) >= 2
            or local_controller.close_enemy_production
            or local_controller.time > 145
        )

    async def handle(self):
        """Places the pool"""
        build = await self.controller.place_building(SPAWNINGPOOL)
        if not build:
            return False
        return True
