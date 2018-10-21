"""Upgrading ov speed"""
from sc2.constants import OVERLORDSPEED, RESEARCH_PNEUMATIZEDCARAPACE


class UpgradePneumatizedCarapace:
    """Ok for now, maybe use overlord speed more and upgrade it earlier"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        return (
            local_controller.caverns
            and local_controller.hatcheries
            and not local_controller.already_pending_upgrade(OVERLORDSPEED)
            and local_controller.can_afford(RESEARCH_PNEUMATIZEDCARAPACE)
        )

    async def handle(self, iteration):
        """Execute the action of upgrading overlord speed"""
        local_controller = self.ai
        chosen_base = local_controller.hatcheries.closest_to(local_controller._game_info.map_center)
        local_controller.add_action(chosen_base(RESEARCH_PNEUMATIZEDCARAPACE))
        return True
