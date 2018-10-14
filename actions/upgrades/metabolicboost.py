"""Upgrading zergling speed"""
from sc2.constants import RESEARCH_ZERGLINGMETABOLICBOOST, ZERGLINGMOVEMENTSPEED


class UpgradeMetabolicBoost:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        if not self.ai.pools.ready.idle:
            return False

        return not self.ai.already_pending_upgrade(ZERGLINGMOVEMENTSPEED) and self.ai.can_afford(
            RESEARCH_ZERGLINGMETABOLICBOOST
        )

    async def handle(self, iteration):
        """Execute the action of upgrading zergling speed"""
        pool = self.ai.pools.ready
        self.ai.adding(pool.first(RESEARCH_ZERGLINGMETABOLICBOOST))
        return True
