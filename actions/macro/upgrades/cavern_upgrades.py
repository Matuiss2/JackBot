"""Upgrading ultras special armor and speed"""
from sc2.constants import CHITINOUSPLATING, RESEARCH_CHITINOUSPLATING
from sc2.constants import ANABOLICSYNTHESIS, ULTRALISKCAVERNRESEARCH_EVOLVEANABOLICSYNTHESIS2


class UpgradesFromCavern:
    """Ok for now"""

    def __init__(self, main):
        self.main = main
        self.selected_caverns = self.selected_research = None

    async def should_handle(self):
        """Requirements to upgrade stuff from caverns"""
        self.selected_caverns = self.main.caverns.idle
        if self.main.can_upgrade(CHITINOUSPLATING, RESEARCH_CHITINOUSPLATING, self.selected_caverns):
            self.selected_research = RESEARCH_CHITINOUSPLATING
            return True
        if self.main.can_upgrade(
            ANABOLICSYNTHESIS, ULTRALISKCAVERNRESEARCH_EVOLVEANABOLICSYNTHESIS2, self.selected_caverns
        ):
            self.selected_research = ULTRALISKCAVERNRESEARCH_EVOLVEANABOLICSYNTHESIS2
            return True

    async def handle(self):
        """Execute the action of upgrading ultra armor and speed"""
        self.main.add_action(self.selected_caverns.first(self.selected_research))
        return True
