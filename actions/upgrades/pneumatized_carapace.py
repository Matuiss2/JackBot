"""Upgrading ov speed"""
from sc2.constants import OVERLORDSPEED, RESEARCH_PNEUMATIZEDCARAPACE


class UpgradePneumatizedCarapace:
    """Ok for now, maybe use overlord speed more and upgrade it earlier"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        return (
            self.ai.caverns
            and self.ai.hatcheries
            and not self.ai.already_pending_upgrade(OVERLORDSPEED)
            and self.ai.can_afford(RESEARCH_PNEUMATIZEDCARAPACE)
        )

    async def handle(self, iteration):
        """Execute the action of upgrading overlord speed"""
        chosen_base = self.ai.hatcheries.closest_to(self.ai._game_info.map_center)
        self.ai.adding(chosen_base(RESEARCH_PNEUMATIZEDCARAPACE))
        return True
