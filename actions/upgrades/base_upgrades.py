"""Upgrading ov speed and burrow"""
from sc2.constants import BURROW, OVERLORDSPEED, RESEARCH_BURROW, RESEARCH_PNEUMATIZEDCARAPACE


class UpgradesFromBases:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main
        self.selected_bases = self.selected_research = None

    async def should_handle(self):
        """Requirements to run handle"""
        local_controller = self.controller
        self.selected_bases = local_controller.hatcheries.idle
        if not (len(local_controller.zerglings) >= 19 and not local_controller.close_enemy_production):
            return False
        if local_controller.can_upgrade(BURROW, RESEARCH_BURROW, self.selected_bases):
            self.selected_research = RESEARCH_BURROW
            return True
        if local_controller.caverns and local_controller.can_upgrade(
            OVERLORDSPEED, RESEARCH_PNEUMATIZEDCARAPACE, self.selected_bases
        ):
            self.selected_research = RESEARCH_PNEUMATIZEDCARAPACE
            return True

    async def handle(self):
        """Execute the action of upgrading burrow"""
        self.controller.add_action(self.selected_bases.random(self.selected_research))
        return True
