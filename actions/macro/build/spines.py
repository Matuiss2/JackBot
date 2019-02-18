"""Everything related to building logic for the spines goes here"""
from sc2.constants import SPINECRAWLER


class BuildSpines:
    """New placement untested"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Requirements to build the spines"""
        if (
            len(self.main.spines) < 4
            and self.main.already_pending(SPINECRAWLER) < 2
            and self.main.building_requirement(SPINECRAWLER, self.main.pools.ready)
            and self.main.townhalls
        ):
            return self.main.close_enemy_production or self.main.close_enemies_to_base

    async def handle(self):
        """Build the spines on the first base near the ramp in case there is a proxy"""
        position = self.main.furthest_townhall_to_center.position.towards(self.main.main_base_ramp.depot_in_middle, 14)
        if any(enemy.distance_to(position) < 15 for enemy in self.main.enemies):
            return False
        await self.main.build(SPINECRAWLER, near=position)
        return True
