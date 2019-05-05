"""Upgrading ultras special armor and speed"""
from sc2.constants import AbilityId, UpgradeId


class CavernUpgrades:
    """Ok for now"""

    def __init__(self, main):
        self.main = main
        self.selected_research = None

    async def should_handle(self):
        """Requirements to upgrade stuff from caverns"""
        if self.main.can_upgrade(
            UpgradeId.CHITINOUSPLATING, AbilityId.RESEARCH_CHITINOUSPLATING, self.main.caverns.idle
        ):
            self.selected_research = AbilityId.RESEARCH_CHITINOUSPLATING
            return True
        if self.main.can_upgrade(
            UpgradeId.ANABOLICSYNTHESIS,
            AbilityId.ULTRALISKCAVERNRESEARCH_EVOLVEANABOLICSYNTHESIS2,
            self.main.caverns.idle,
        ):
            self.selected_research = AbilityId.ULTRALISKCAVERNRESEARCH_EVOLVEANABOLICSYNTHESIS2
            return True

    async def handle(self):
        """Execute the action of upgrading ultra armor and speed"""
        self.main.add_action(self.main.caverns.idle.first(self.selected_research))
