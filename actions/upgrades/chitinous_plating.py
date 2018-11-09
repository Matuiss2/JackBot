"""Upgrading ultras special armor"""
from sc2.constants import CHITINOUSPLATING, RESEARCH_CHITINOUSPLATING


class UpgradeChitinousPlating:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        return local_controller.caverns and local_controller.can_upgrade(CHITINOUSPLATING, CHITINOUSPLATING)

    async def handle(self, iteration):
        """Execute the action of upgrading ultra armor"""
        local_controller = self.ai
        local_controller.add_action(local_controller.caverns.idle.first(RESEARCH_CHITINOUSPLATING))
        return True
