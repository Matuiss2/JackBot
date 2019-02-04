"""Upgrading ov speed and burrow"""
from sc2.constants import BURROW, OVERLORDSPEED, RESEARCH_BURROW, RESEARCH_PNEUMATIZEDCARAPACE


class UpgradesFromBases:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main
        self.selected_bases = self.selected_research = None

    async def should_handle(self):
        """Requirements to upgrade stuff from bases"""
        self.selected_bases = self.controller.hatcheries.idle
        if self.controller.zergling_amount <= 19 and not self.controller.close_enemy_production:
            return False
        if self.controller.can_upgrade(BURROW, RESEARCH_BURROW, self.selected_bases):
            self.selected_research = RESEARCH_BURROW
            return True
        if self.controller.caverns and self.controller.can_upgrade(
            OVERLORDSPEED, RESEARCH_PNEUMATIZEDCARAPACE, self.selected_bases
        ):
            self.selected_research = RESEARCH_PNEUMATIZEDCARAPACE
            return True

    async def handle(self):
        """Execute the action of upgrading burrow or ov speed"""
        self.controller.add_action(self.selected_bases.random(self.selected_research))
        return True
