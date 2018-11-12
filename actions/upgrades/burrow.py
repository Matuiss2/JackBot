"""Upgrading burrow"""
from sc2.constants import BURROW, RESEARCH_BURROW


class UpgradeBurrow:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        return (
            len(local_controller.zerglings) >= 19
            and (not local_controller.close_enemies_to_base or local_controller.time > 300)
            and (not local_controller.close_enemy_production or local_controller.time > 300)
            and local_controller.hatcheries.idle
            and local_controller.can_upgrade(BURROW, RESEARCH_BURROW)
        )

    async def handle(self, iteration):
        """Execute the action of upgrading burrow"""
        local_controller = self.ai
        chosen_base = local_controller.hatcheries.idle.closest_to(local_controller.game_info.map_center)
        local_controller.add_action(chosen_base(RESEARCH_BURROW))
        return True
