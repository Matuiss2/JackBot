"""Upgrading ultras special armor"""
from sc2.constants import ANABOLICSYNTHESIS, ULTRALISKCAVERNRESEARCH_EVOLVEANABOLICSYNTHESIS2


class UpgradeChitinousPlating:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main
        self.selected_caverns = None

    async def should_handle(self):
        """Requirements to run handle"""
        local_controller = self.controller
        self.selected_caverns = local_controller.caverns.idle
        return local_controller.can_upgrade(
            ANABOLICSYNTHESIS, ULTRALISKCAVERNRESEARCH_EVOLVEANABOLICSYNTHESIS2, self.selected_caverns
        )

    async def handle(self):
        """Execute the action of upgrading ultra armor"""
        self.controller.add_action(self.selected_caverns.first(ULTRALISKCAVERNRESEARCH_EVOLVEANABOLICSYNTHESIS2))
        return True
