"""Upgrading ov speed"""
from sc2.constants import OVERLORDSPEED, RESEARCH_PNEUMATIZEDCARAPACE


class UpgradePneumatizedCarapace:
    """Ok for now, maybe use overlord speed more and upgrade it earlier once our bots gets even more reactive"""

    def __init__(self, main):
        self.controller = main
        self.selected_bases = None

    async def should_handle(self):
        """Requirements to run handle"""
        local_controller = self.controller
        self.selected_bases = local_controller.hatcheries.idle
        return local_controller.caverns and local_controller.can_upgrade(
            OVERLORDSPEED, RESEARCH_PNEUMATIZEDCARAPACE, self.selected_bases
        )

    async def handle(self):
        """Execute the action of upgrading overlord speed"""
        self.controller.add_action(self.selected_bases.random(RESEARCH_PNEUMATIZEDCARAPACE))
        return True
