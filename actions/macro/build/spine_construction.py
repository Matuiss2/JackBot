"""Everything related to building logic for the spines goes here"""
from sc2.constants import UnitTypeId


class SpineConstruction:
    """New placement untested"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Requirements to build the spines"""
        if (
            len(self.main.spines) < 4
            and self.main.already_pending(UnitTypeId.SPINECRAWLER) < 2
            and self.main.building_requirement(UnitTypeId.SPINECRAWLER, self.main.pools.ready)
            and self.main.townhalls
        ):
            return self.main.close_enemy_production or self.main.close_enemies_to_base

    async def handle(self):
        """Build the spines on the first base near the ramp in case there is a proxy"""
        position = self.main.furthest_townhall_to_center.position.towards(self.main.main_base_ramp.depot_in_middle, 14)
        if not any(enemy.distance_to(position) < 13 for enemy in self.main.enemies):
            await self.main.build(UnitTypeId.SPINECRAWLER, near=position)
