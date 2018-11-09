"""Upgrading zerglings atk speed"""
from sc2.constants import RESEARCH_ZERGLINGADRENALGLANDS, ZERGLINGATTACKSPEED


class UpgradeAdrenalGlands:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        if not local_controller.pools.ready.idle:
            return False

        return (
            local_controller.can_upgrade(ZERGLINGATTACKSPEED, RESEARCH_ZERGLINGADRENALGLANDS) and local_controller.hives
        )

    async def handle(self, iteration):
        """Execute the action of upgrading zergling atk speed"""
        local_controller = self.ai
        pool = local_controller.pools.ready
        local_controller.add_action(pool.first(RESEARCH_ZERGLINGADRENALGLANDS))
        return True
