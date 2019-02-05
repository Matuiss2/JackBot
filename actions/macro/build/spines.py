"""Everything related to building logic for the spines goes here"""
from sc2.constants import SPINECRAWLER


class BuildSpines:
    """New placement untested"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Requirements to build the spines"""
        return (
            self.main.building_requirement(SPINECRAWLER, self.main.pools.ready)
            and self.main.townhalls
            and self.main.close_enemy_production
            and len(self.main.spines) < 4
            and self.main.already_pending(SPINECRAWLER) < 2
        )

    async def handle(self):
        """Build the spines on the first base near the ramp in case there is a proxy"""
        await self.main.build(
            SPINECRAWLER,
            near=self.main.furthest_townhall_to_center.position.towards(self.main.main_base_ramp.depot_in_middle, 14),
        )
        return True
