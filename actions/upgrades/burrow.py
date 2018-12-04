"""Upgrading burrow"""
from sc2.constants import BURROW, RESEARCH_BURROW


class UpgradeBurrow:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai
        self.selected_bases = None

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        self.selected_bases = local_controller.hatcheries.idle
        return (
            len(local_controller.zerglings) >= 19
            and (
                all(False for _ in (local_controller.close_enemies_to_base, local_controller.close_enemy_production))
                or local_controller.time >= 300
            )
            and local_controller.can_upgrade(BURROW, RESEARCH_BURROW, self.selected_bases)
        )

    async def handle(self, iteration):
        """Execute the action of upgrading burrow"""
        local_controller = self.ai
        local_controller.add_action(
            self.selected_bases.closest_to(local_controller.game_info.map_center)(RESEARCH_BURROW)
        )
        return True
