"""Upgrading burrow"""
from sc2.constants import BURROW, RESEARCH_BURROW


class UpgradeBurrow:
    """Ok for now, didn't find a way to use it tho"""

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
            and not local_controller.already_pending_upgrade(BURROW)
            and local_controller.can_afford(RESEARCH_BURROW)
        )

    async def handle(self, iteration):
        """Execute the action of upgrading burrow"""
        local_controller = self.ai
        chosen_base = local_controller.hatcheries.idle.closest_to(local_controller._game_info.map_center)
        local_controller.add_action(chosen_base(RESEARCH_BURROW))
        return True
