"""Upgrading ov speed and burrow"""
from sc2.constants import BURROW, OVERLORDSPEED, RESEARCH_BURROW, RESEARCH_PNEUMATIZEDCARAPACE


class UpgradesFromBases:
    """Ok for now"""

    def __init__(self, main):
        self.main = main
        self.selected_research = None

    async def should_handle(self):
        """Requirements to upgrade stuff from bases"""
        if self.main.zergling_amount <= 19 and not self.main.close_enemy_production:
            return False
        if self.main.can_upgrade(BURROW, RESEARCH_BURROW, self.main.hatcheries.idle):
            self.selected_research = RESEARCH_BURROW
            return True
        if self.main.caverns and self.main.can_upgrade(
            OVERLORDSPEED, RESEARCH_PNEUMATIZEDCARAPACE, self.main.hatcheries.idle
        ):
            self.selected_research = RESEARCH_PNEUMATIZEDCARAPACE
            return True

    async def handle(self):
        """Execute the action of upgrading burrow or ov speed"""
        self.main.add_action(self.main.hatcheries.idle.random(self.selected_research))
        return True
