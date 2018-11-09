"""Upgrading zergling speed"""
from sc2.constants import RESEARCH_ZERGLINGMETABOLICBOOST, ZERGLINGMOVEMENTSPEED


class UpgradeMetabolicBoost:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        if not local_controller.pools.ready.idle:
            return False

        return local_controller.can_upgrade(ZERGLINGMOVEMENTSPEED, RESEARCH_ZERGLINGMETABOLICBOOST)

    async def handle(self, iteration):
        """Execute the action of upgrading zergling speed"""
        local_controller = self.ai
        pool = local_controller.pools.ready
        local_controller.add_action(pool.first(RESEARCH_ZERGLINGMETABOLICBOOST))
        return True
