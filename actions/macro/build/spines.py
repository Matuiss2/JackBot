"""Everything related to building logic for the spines goes here"""
from sc2.constants import SPINECRAWLER


class BuildSpines:
    """New placement untested"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Requirements to build the spines"""
        return (
            self.controller.building_requirement(SPINECRAWLER, self.controller.pools.ready)
            and self.controller.townhalls
            and self.controller.close_enemy_production
            and len(self.controller.spines) < 4
            and self.controller.already_pending(SPINECRAWLER) < 2
        )

    async def handle(self):
        """Build the spines on the first base near the ramp in case there is a proxy"""
        await self.controller.build(
            SPINECRAWLER,
            near=self.controller.furthest_townhall_to_center.position.towards(
                self.controller.main_base_ramp.depot_in_middle, 14
            ),
        )
        return True
