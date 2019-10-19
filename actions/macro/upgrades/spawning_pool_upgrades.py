"""Upgrading zerglings atk-speed and speed"""
from sc2.constants import AbilityId
from sc2.ids.upgrade_id import UpgradeId


class SpawningPoolUpgrades:
    """Ok for now"""

    def __init__(self, main):
        self.main = main
        self.available_pool = self.selected_research = None

    async def should_handle(self):
        """Requirements to upgrade stuff from pools"""
        self.available_pool = self.main.settled_pool.idle
        if self.main.can_upgrade(
            UpgradeId.ZERGLINGMOVEMENTSPEED, AbilityId.RESEARCH_ZERGLINGMETABOLICBOOST, self.available_pool
        ):
            self.selected_research = AbilityId.RESEARCH_ZERGLINGMETABOLICBOOST
            return True
        if (
            self.main.can_upgrade(
                UpgradeId.ZERGLINGATTACKSPEED, AbilityId.RESEARCH_ZERGLINGADRENALGLANDS, self.available_pool
            )
            and self.main.hives
        ):
            self.selected_research = AbilityId.RESEARCH_ZERGLINGADRENALGLANDS
            return True

    async def handle(self):
        """Execute the action of upgrading zergling atk-speed and speed"""
        self.main.add_action(self.available_pool.first(self.selected_research))
