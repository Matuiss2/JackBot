"""Upgrading zerglings atk-speed and speed"""
from sc2.constants import (
    RESEARCH_ZERGLINGADRENALGLANDS,
    RESEARCH_ZERGLINGMETABOLICBOOST,
    ZERGLINGATTACKSPEED,
    ZERGLINGMOVEMENTSPEED,
)


class UpgradesFromSpawningPool:
    """Ok for now"""

    def __init__(self, main):
        self.main = main
        self.selected_pools = self.selected_research = None

    async def should_handle(self):
        """Requirements to upgrade stuff from pools"""
        self.selected_pools = self.main.pools.ready.idle
        if self.main.can_upgrade(ZERGLINGMOVEMENTSPEED, RESEARCH_ZERGLINGMETABOLICBOOST, self.selected_pools):
            self.selected_research = RESEARCH_ZERGLINGMETABOLICBOOST
            return True
        if (
            self.main.can_upgrade(ZERGLINGATTACKSPEED, RESEARCH_ZERGLINGADRENALGLANDS, self.selected_pools)
            and self.main.hives
        ):
            self.selected_research = RESEARCH_ZERGLINGADRENALGLANDS
            return True

    async def handle(self):
        """Execute the action of upgrading zergling atk-speed and speed"""
        self.main.add_action(self.selected_pools.first(self.selected_research))
        return True
