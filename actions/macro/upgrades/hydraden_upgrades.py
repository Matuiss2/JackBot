"""Upgrading hydras speed and range"""
from sc2.constants import AbilityId, UpgradeId


class HydradenUpgrades:
    """Ok for now"""

    def __init__(self, main):
        self.main = main
        self.selected_research = self.available_hydraden = None

    async def should_handle(self):
        """Requirements to upgrade stuff from hydradens"""
        self.available_hydraden = self.main.settled_hydraden.idle
        if self.main.floated_buildings_bm:
            return False
        if self.main.can_upgrade(
            UpgradeId.EVOLVEGROOVEDSPINES, AbilityId.RESEARCH_GROOVEDSPINES, self.available_hydraden
        ):
            self.selected_research = AbilityId.RESEARCH_GROOVEDSPINES
            return True
        if (
            self.main.can_upgrade(
                UpgradeId.EVOLVEMUSCULARAUGMENTS, AbilityId.RESEARCH_MUSCULARAUGMENTS, self.available_hydraden
            )
            and self.main.hydra_range
        ):
            self.selected_research = AbilityId.RESEARCH_MUSCULARAUGMENTS
            return True

    async def handle(self):
        """Execute the action of upgrading hydras speed and range"""
        self.main.add_action(self.available_hydraden.first(self.selected_research))
