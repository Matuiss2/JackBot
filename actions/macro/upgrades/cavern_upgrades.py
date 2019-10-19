"""Upgrading ultras special armor and speed"""
from sc2.constants import AbilityId
from sc2.ids.upgrade_id import UpgradeId


class CavernUpgrades:
    """Ok for now"""

    def __init__(self, main):
        self.main = main
        self.available_cavern = self.selected_research = None

    async def should_handle(self):
        """Requirements to upgrade stuff from caverns"""
        self.available_cavern = self.main.caverns.idle
        if self.main.can_upgrade(
            UpgradeId.CHITINOUSPLATING, AbilityId.RESEARCH_CHITINOUSPLATING, self.available_cavern
        ):
            self.selected_research = AbilityId.RESEARCH_CHITINOUSPLATING
            return True
        if self.main.can_upgrade(
            UpgradeId.ANABOLICSYNTHESIS, AbilityId.RESEARCH_ANABOLICSYNTHESIS, self.available_cavern
        ):
            self.selected_research = AbilityId.RESEARCH_ANABOLICSYNTHESIS
            return True

    async def handle(self):
        """Execute the action of upgrading ultra armor and speed"""
        self.main.add_action(self.available_cavern.first(self.selected_research))
