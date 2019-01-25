"""Upgrading ultras special armor and speed"""
from sc2.constants import CHITINOUSPLATING, RESEARCH_CHITINOUSPLATING
from sc2.constants import ANABOLICSYNTHESIS, ULTRALISKCAVERNRESEARCH_EVOLVEANABOLICSYNTHESIS2


class UpgradesFromCavern:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main
        self.selected_caverns = self.selected_research = None

    async def should_handle(self):
        """Requirements to run handle"""
        local_controller = self.controller
        self.selected_caverns = local_controller.caverns.idle.noqueue
        if local_controller.can_upgrade(CHITINOUSPLATING, RESEARCH_CHITINOUSPLATING, self.selected_caverns):
            self.selected_research = RESEARCH_CHITINOUSPLATING
            return True
        if local_controller.can_upgrade(
            ANABOLICSYNTHESIS, ULTRALISKCAVERNRESEARCH_EVOLVEANABOLICSYNTHESIS2, self.selected_caverns
        ):
            self.selected_research = ULTRALISKCAVERNRESEARCH_EVOLVEANABOLICSYNTHESIS2
            return True

    async def handle(self):
        """Execute the action of upgrading ultra armor"""
        self.controller.add_action(self.selected_caverns.first(self.selected_research))
        return True
