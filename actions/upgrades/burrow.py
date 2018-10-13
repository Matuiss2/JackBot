"""Upgrading burrow"""
from sc2.constants import BURROW, RESEARCH_BURROW


class UpgradeBurrow:
    """Ok for now, didn't find a way to use it tho"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        return (
            self.ai.lairs
            and self.ai.hatcheries.idle
            and not self.ai.already_pending_upgrade(BURROW)
            and self.ai.can_afford(RESEARCH_BURROW)
        )

    async def handle(self, iteration):
        """Execute the action of upgrading burrow"""
        chosen_base = self.ai.hatcheries.idle.closest_to(self.ai._game_info.map_center)
        self.ai.actions.append(chosen_base(RESEARCH_BURROW))
        return True
