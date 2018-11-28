"""Upgrading burrow"""
from sc2.constants import BURROW, RESEARCH_BURROW


class UpgradeBurrow:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        five_minutes_trigger = local_controller.time >= 300
        return (
            len(local_controller.zerglings) >= 19
            and (not local_controller.close_enemies_to_base or five_minutes_trigger)
            and (not local_controller.close_enemy_production or five_minutes_trigger)
            and local_controller.hatcheries.idle
            and local_controller.can_upgrade(BURROW, RESEARCH_BURROW)
        )

    async def handle(self, iteration):
        """Execute the action of upgrading burrow"""
        local_controller = self.ai
        local_controller.add_action(
            local_controller.hatcheries.idle.closest_to(local_controller.game_info.map_center)(RESEARCH_BURROW)
        )
        return True
