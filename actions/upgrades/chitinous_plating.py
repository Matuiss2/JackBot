"""Upgrading ultras special armor"""
from sc2.constants import CHITINOUSPLATING, RESEARCH_CHITINOUSPLATING


class UpgradeChitinousPlating:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        return (
            self.ai.caverns
            and not self.ai.already_pending_upgrade(CHITINOUSPLATING)
            and self.ai.can_afford(CHITINOUSPLATING)
        )

    async def handle(self, iteration):
        """Execute the action of upgrading ultra armor"""
        self.ai.adding(self.ai.caverns.idle.first(RESEARCH_CHITINOUSPLATING))
        return True
