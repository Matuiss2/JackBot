"""Upgrading ultras special armor"""
from sc2.constants import CHITINOUSPLATING, RESEARCH_CHITINOUSPLATING


class UpgradeChitinousPlating:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai
        self.selected_caverns = None

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        self.selected_caverns = local_controller.caverns
        return local_controller.can_upgrade(CHITINOUSPLATING, CHITINOUSPLATING, self.selected_caverns)

    async def handle(self, iteration):
        """Execute the action of upgrading ultra armor"""
        local_controller = self.ai
        local_controller.add_action(self.selected_caverns.idle.first(RESEARCH_CHITINOUSPLATING))
        return True
