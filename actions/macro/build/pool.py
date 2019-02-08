"""Everything related to building logic for the pools goes here"""
from sc2.constants import SPAWNINGPOOL


class BuildPool:
    """Ok for now"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Requirement for building the spawning pool"""
        return self.main.can_build_unique(SPAWNINGPOOL, self.main.pools) and (
            self.main.base_amount >= 2 or self.main.close_enemy_production or self.main.time > 145
        )

    async def handle(self):
        """Places the pool"""
        await self.main.place_building(SPAWNINGPOOL)
        return True
