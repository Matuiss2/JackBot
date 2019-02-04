"""Everything related to building logic for the pools goes here"""
from sc2.constants import SPAWNINGPOOL


class BuildPool:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Requirement for building the spawning pool"""
        return self.controller.can_build_unique(SPAWNINGPOOL, self.controller.pools) and (
            self.controller.base_amount >= 2 or self.controller.close_enemy_production or self.controller.time > 145
        )

    async def handle(self):
        """Places the pool"""
        build = await self.controller.place_building(SPAWNINGPOOL)
        if not build:
            return False
        return True
