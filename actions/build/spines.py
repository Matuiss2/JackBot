"""Everything related to building logic for the spines goes here"""
from sc2.constants import SPINECRAWLER


class BuildSpines:
    """New placement untested"""

    def __init__(self, ai):
        self.ai = ai
        self.lairs = None

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        if not self.ai.pools.ready:
            return False

        return self.ai.close_enemy_production and len(self.ai.spines) < 4 and self.ai.already_pending(SPINECRAWLER) < 2

    async def handle(self, iteration):
        """Build the spines on the first base near the ramp in case there is a proxy"""
        if self.ai.townhalls:
            await self.ai.build(
                SPINECRAWLER,
                near=self.ai.townhalls.furthest_to(self.ai._game_info.map_center).position.towards(
                    self.ai.main_base_ramp.depot_in_middle, 14
                ),
            )
            return True
