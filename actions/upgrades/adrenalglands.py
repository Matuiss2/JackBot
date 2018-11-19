"""Upgrading zerglings atk speed"""
from sc2.constants import RESEARCH_ZERGLINGADRENALGLANDS, ZERGLINGATTACKSPEED


class UpgradeAdrenalGlands:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        return (
            local_controller.pools.ready.idle
            and local_controller.can_upgrade(ZERGLINGATTACKSPEED, RESEARCH_ZERGLINGADRENALGLANDS)
            and local_controller.hives
        )

    async def handle(self, iteration):
        """Execute the action of upgrading zergling atk speed"""
        local_controller = self.ai
        local_controller.add_action(local_controller.pools.ready.first(RESEARCH_ZERGLINGADRENALGLANDS))
        return True
