"""Everything related to building logic for the spines goes here"""
from sc2.constants import UnitTypeId


class SpineConstruction:
    """New placement untested"""

    def __init__(self, main):
        self.main = main
        self.placement_position = None

    async def should_handle(self):
        """Requirements to build the spines"""
        if (
            len(self.main.spines) < 4
            and self.main.already_pending(UnitTypeId.SPINECRAWLER) < 2
            and self.main.building_requirements(UnitTypeId.SPINECRAWLER, self.main.settled_pool)
            and self.main.townhalls
        ):
            self.placement_position = self.main.furthest_townhall_to_center.position.towards(
                self.main.main_base_ramp.depot_in_middle, 14
            )
            return (self.main.close_enemy_production or self.main.close_enemies_to_base) and not any(
                enemy.distance_to(self.placement_position) < 13 for enemy in self.main.enemies
            )

    async def handle(self):
        """Build the spines on the first base near the ramp in case there is a proxy"""
        await self.main.build(UnitTypeId.SPINECRAWLER, near=self.placement_position)
