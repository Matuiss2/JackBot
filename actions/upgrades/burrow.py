"""Upgrading burrow"""
from sc2.constants import BURROW, RESEARCH_BURROW


class UpgradeBurrow:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai
        self.selected_bases = None

    async def should_handle(self):
        """Requirements to run handle"""
        local_controller = self.ai
        self.selected_bases = local_controller.hatcheries.idle
        return (
            len(local_controller.zerglings) >= 19
            and (
                all(
                    not flag
                    for flag in (local_controller.close_enemies_to_base, local_controller.close_enemy_production)
                )
                or local_controller.time >= 300
            )
            and local_controller.can_upgrade(BURROW, RESEARCH_BURROW, self.selected_bases)
        )

    async def handle(self):
        """Execute the action of upgrading burrow"""
        self.ai.add_action(self.selected_bases.random(RESEARCH_BURROW))
        return True
